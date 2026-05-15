#!/usr/bin/env python3
"""Query OpenAlex API for recent sEMG/SSI papers, filter already sent ones."""
import json
import sys
import subprocess
import urllib.parse

SENT_PAPERS_FILE = "/Users/rayopenclaw/ray-agent/sent_papers.json"

QUERIES = [
    "sEMG silent speech recognition",
    "facial electromyography silent speech interface",
]

FIELDS = "title,publication_date,doi,abstract_inverted_index,authorships,primary_location,open_access"

def search_openalex(query, max_results=15):
    params = urllib.parse.urlencode({
        "search": query,
        "filter": "from_publication_date:2023-01-01",
        "sort": "publication_date:desc",
        "per-page": max_results,
        "select": FIELDS,
        "mailto": "rayopenclaw316@gmail.com",
    })
    url = f"https://api.openalex.org/works?{params}"
    # 使用 curl 避免 cron 環境 DNS 解析失敗
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

def parse_results(data):
    entries = []
    for item in data.get("results", []):
        title = item.get("title", "").strip()
        if not title:
            continue
        abstract = reconstruct_abstract(item.get("abstract_inverted_index") or {})
        published = (item.get("publication_date") or "")[:10]
        doi = item.get("doi") or ""
        openalex_id = item.get("id") or ""
        link = doi if doi else openalex_id
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
        })
    return entries

def main():
    try:
        with open(SENT_PAPERS_FILE) as f:
            sent = set(json.load(f).get("sent_papers", []))
    except Exception:
        sent = set()

    seen_titles = set()
    results = []
    for q in QUERIES:
        try:
            data = search_openalex(q)
            for e in parse_results(data):
                if e["title"] not in sent and e["title"] not in seen_titles:
                    seen_titles.add(e["title"])
                    results.append(e)
        except Exception as err:
            print(f"搜尋失敗（{q}）：{err}", file=sys.stderr)

    if not results:
        print("未找到新論文。", file=sys.stderr)
        sys.exit(1)

    print(f"找到 {len(results)} 篇未推送過的論文：\n")
    for i, p in enumerate(results[:10], 1):
        print(f"## 論文 {i}")
        print(f"標題：{p['title']}")
        print(f"作者：{', '.join(p['authors'])}")
        print(f"發表日期：{p['published']}")
        print(f"摘要：{p['abstract']}")
        print(f"連結：{p['link']}")
        print()

if __name__ == "__main__":
    main()
