#!/usr/bin/env python3
"""Query OpenAlex + Semantic Scholar for recent sEMG/SSI/Chinese-silent-speech papers."""
import json
import sys
import subprocess
import urllib.parse
import time

SENT_PAPERS_FILE = "/Users/rayopenclaw/ray-agent/sent_papers.json"

# 相關性過濾：必須同時滿足「有 EMG/訊號詞」AND「有應用詞」，或包含明確短語
EMG_TERMS = [
    "emg", "electromyography", "myoelectric",
    "semg", "s-emg", "surface emg",
]
APP_TERMS = [
    "speech", "silent", "articulat",
    "gesture", "prosthes", "lip ", "facial",
    "mandarin", "chinese",
]
EXACT_PHRASES = [
    "silent speech interface",
    "silent speech recognition",
    "silent speech decoding",
    "eeg silent speech",
    "eeg speech decoding",
    "eeg speech interface",
    "chinese silent",
    "facial emg",
    "lip emg",
    "speech emg",
    "emg speech",
    "semg speech",
    "brain-computer interface speech",
]

def is_relevant(title: str, abstract: str) -> bool:
    text = (title + " " + abstract).lower()
    # 命中任何精確短語 → 直接通過
    if any(p in text for p in EXACT_PHRASES):
        return True
    # 同時有 EMG 詞 AND 應用詞 → 通過
    has_emg = any(t in text for t in EMG_TERMS)
    has_app = any(t in text for t in APP_TERMS)
    return has_emg and has_app

# OpenAlex 查詢詞
OPENALEX_QUERIES = [
    "sEMG silent speech recognition",
    "facial electromyography silent speech interface",
    "Chinese silent speech EMG",
    "silent speech interface deep learning",
    "surface EMG gesture speech classification",
]

# Semantic Scholar 查詢詞（涵蓋 IEEE、Elsevier、arXiv）
SEMANTIC_QUERIES = [
    "facial EMG silent speech Chinese",
    "Mandarin speech electromyography recognition",
    "silent speech interface neural decoding",
    "articulatory gesture EMG recognition",
    "lip EMG speech synthesis",
    "sEMG speech prosthesis deep learning",
]

# ── OpenAlex ──────────────────────────────────────────────

OPENALEX_FIELDS = "title,publication_date,doi,abstract_inverted_index,authorships"

def search_openalex(query, max_results=15):
    params = urllib.parse.urlencode({
        "search": query,
        "filter": "from_publication_date:2023-01-01",
        "sort": "publication_date:desc",
        "per-page": max_results,
        "select": OPENALEX_FIELDS,
        "mailto": "rayopenclaw316@gmail.com",
    })
    url = f"https://api.openalex.org/works?{params}"
    result = subprocess.run(
        ["curl", "-s", "--max-time", "30",
         "-H", "User-Agent: python-urllib/3", url],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"curl 失敗（exit {result.returncode}）：{result.stderr.strip()}")
    return json.loads(result.stdout)

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    positions = []
    for word, pos_list in inverted_index.items():
        for pos in pos_list:
            positions.append((pos, word))
    positions.sort()
    return " ".join(word for _, word in positions)

def parse_openalex(data):
    entries = []
    for item in data.get("results", []):
        title = item.get("title", "").strip()
        if not title:
            continue
        abstract = reconstruct_abstract(item.get("abstract_inverted_index") or {})
        published = (item.get("publication_date") or "")[:10]
        doi = item.get("doi") or ""
        link = doi if doi else ""
        authors = [
            a["author"]["display_name"]
            for a in (item.get("authorships") or [])[:3]
            if a.get("author", {}).get("display_name")
        ]
        entries.append({
            "title": title,
            "abstract": abstract[:1000],
            "link": link,
            "published": published,
            "authors": authors,
            "source": "OpenAlex",
        })
    return entries

# ── Semantic Scholar ──────────────────────────────────────

def search_semantic(query, max_results=10):
    params = urllib.parse.urlencode({
        "query": query,
        "fields": "title,abstract,authors,publicationDate,externalIds,openAccessPdf,url",
        "limit": max_results,
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    result = subprocess.run(
        ["curl", "-s", "--max-time", "30",
         "-H", "User-Agent: python-requests/2.28", url],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"curl 失敗（exit {result.returncode}）：{result.stderr.strip()}")
    return json.loads(result.stdout)

def parse_semantic(data):
    entries = []
    for item in data.get("data", []):
        title = (item.get("title") or "").strip()
        if not title:
            continue
        abstract = (item.get("abstract") or "")[:1000]
        published = (item.get("publicationDate") or "")[:10]

        # 取得連結：優先 DOI，其次 PDF，最後 S2 頁面
        ext = item.get("externalIds") or {}
        doi = ext.get("DOI") or ""
        pdf = (item.get("openAccessPdf") or {}).get("url") or ""
        s2_url = item.get("url") or ""
        link = f"https://doi.org/{doi}" if doi else (pdf or s2_url)

        authors = [
            a["name"] for a in (item.get("authors") or [])[:3]
            if a.get("name")
        ]
        entries.append({
            "title": title,
            "abstract": abstract,
            "link": link,
            "published": published,
            "authors": authors,
            "source": "Semantic Scholar",
        })
    return entries

# ── 主程式 ────────────────────────────────────────────────

def main():
    try:
        with open(SENT_PAPERS_FILE) as f:
            sent = set(json.load(f).get("sent_papers", []))
    except Exception:
        sent = set()

    seen_titles = set()
    results = []

    # OpenAlex 搜尋
    for q in OPENALEX_QUERIES:
        try:
            data = search_openalex(q)
            for e in parse_openalex(data):
                if not is_relevant(e["title"], e["abstract"]):
                    continue
                if e["title"] not in sent and e["title"] not in seen_titles:
                    seen_titles.add(e["title"])
                    results.append(e)
        except Exception as err:
            print(f"[OpenAlex] 搜尋失敗（{q}）：{err}", file=sys.stderr)

    # Semantic Scholar 搜尋（3 秒間隔避免 rate limit，無 key 限制 100 req/5min）
    for q in SEMANTIC_QUERIES:
        try:
            time.sleep(3)
            data = search_semantic(q)
            for e in parse_semantic(data):
                if not is_relevant(e["title"], e["abstract"]):
                    continue
                if e["title"] not in sent and e["title"] not in seen_titles:
                    seen_titles.add(e["title"])
                    results.append(e)
        except Exception as err:
            print(f"[Semantic Scholar] 搜尋失敗（{q}）：{err}", file=sys.stderr)

    if not results:
        print("未找到新論文。", file=sys.stderr)
        sys.exit(1)

    # 依發表日期排序（最新優先）
    results.sort(key=lambda x: x["published"] or "0000", reverse=True)

    print(f"找到 {len(results)} 篇未推送過的論文：\n")
    for i, p in enumerate(results[:15], 1):
        print(f"## 論文 {i}（{p['source']}）")
        print(f"標題：{p['title']}")
        print(f"作者：{', '.join(p['authors'])}")
        print(f"發表日期：{p['published']}")
        print(f"摘要：{p['abstract']}")
        print(f"連結：{p['link']}")
        print()

if __name__ == "__main__":
    main()
