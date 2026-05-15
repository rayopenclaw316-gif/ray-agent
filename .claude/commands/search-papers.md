---
description: 搜尋最新 sEMG 無聲語音介面相關論文，排除已傳過的論文，並透過 Discord 傳送摘要
argument-hint: [可選：額外關鍵字，例如 "transformer" 或 "Chinese"]
---

你是陳睿莆的研究助理。請完成以下論文搜尋任務：

## Step 1：讀取已傳論文清單

讀取 `/Users/rayopenclaw/Downloads/ray-agent/sent_papers.json`，取得 `sent_papers` 陣列作為排除清單。

## Step 2：使用 Firecrawl 搜尋論文（執行兩次）

搜尋 1：關鍵字 "facial EMG sEMG silent speech recognition deep learning neural network 2024 2025 $ARGUMENTS"
搜尋 2：關鍵字 "facial electromyography silent speech interface transformer CNN 2024 2025 $ARGUMENTS"

## Step 3：整理 3～5 篇最相關且未曾傳送過的論文

**排除 Step 1 清單中的所有論文，不可重複推薦。**

每篇論文需包含：
1. 標題（英文）
2. 來源（IEEE / ScienceDirect / Springer / 其他）
3. 研究目標：2～3 句繁體中文說明
4. 使用技術：列出方法並附中文解釋
5. 研究意義：對無聲語音介面（SSI）的貢獻
6. 連結

## Step 4：透過 Discord 傳送摘要

將摘要透過以下指令傳送到 Discord：
```
echo "[摘要內容]" | python3 /Users/rayopenclaw/Downloads/ray-agent/discord_send.py
```

## Step 5：更新已傳論文清單

將本次推薦的論文標題加入 `/Users/rayopenclaw/Downloads/ray-agent/sent_papers.json` 的 `sent_papers` 陣列。

## 規則
- 全程使用繁體中文
- 每個英文技術術語必須附中文解釋
- 完成後回報「已傳送 N 篇論文摘要至 Discord，已更新排除清單」
