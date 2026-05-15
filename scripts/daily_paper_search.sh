#!/bin/bash
# 每日論文摘要腳本 - 台灣時間早上 8:00 自動執行
# 使用 arXiv API 搜尋、Claude 撰寫摘要、Discord Bot 傳訊息

export PATH="/Applications/cmux.app/Contents/Resources/bin:/Users/rayopenclaw/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/Users/rayopenclaw"

LOG="/Users/rayopenclaw/ray-agent/logs/paper_search.log"
mkdir -p "$(dirname "$LOG")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 腳本啟動" >> "$LOG"

# HOME 已設定，claude CLI 會自動從 Keychain 讀取 OAuth 憑證並處理 token 刷新
# 不設 ANTHROPIC_API_KEY，避免短期 accessToken 過期導致 401

BASE="/Users/rayopenclaw/ray-agent"
SENT_PAPERS_FILE="$BASE/sent_papers.json"

# Step 1: 用 arXiv API 取得論文清單
PAPERS=$(python3 "$BASE/scripts/arxiv_search.py" 2>>"$LOG")
if [ $? -ne 0 ] || [ -z "$PAPERS" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 錯誤：arXiv 搜尋失敗，中止執行" >> "$LOG"
  exit 1
fi

# Step 2: 請 Claude 撰寫摘要（不需要搜尋工具）
PROMPT="你是陳睿莆的研究助理。以下是從 arXiv 找到的最新 sEMG / 無聲語音介面相關論文，請從中選出 3～5 篇最相關的，撰寫繁體中文摘要。

$PAPERS

每篇論文需包含：
1. 標題（英文）
2. 來源（arXiv）
3. 研究目標：2～3 句繁體中文說明
4. 使用技術：列出方法並附中文解釋，例如：
   - sEMG（表面肌電圖）：貼在臉部皮膚偵測說話時肌肉的微弱電訊號
   - CNN（卷積神經網路）：自動從訊號中提取空間特徵的深度學習架構
   - Transformer：使用自注意力機制捕捉序列長距離關係的神經網路
   - Transfer Learning（遷移學習）：將大資料集訓練知識應用到小資料集
   - GRU（閘控遞迴單元）：處理時序資料的輕量化遞迴神經網路
5. 研究意義：對無聲語音介面（SSI）的貢獻
6. 連結

在摘要最後加上以下區塊，列出本次推薦論文的英文標題（純文字，每行一篇）：
SENT_TITLES_START
[論文標題1]
[論文標題2]
...
SENT_TITLES_END

規則：全程繁體中文，每個英文技術術語必須附中文解釋，只需輸出格式化的論文摘要文字即可。"

OUTPUT=$( /Applications/cmux.app/Contents/Resources/bin/claude -p "$PROMPT" \
  --output-format text \
  --dangerously-skip-permissions 2>&1 )


# 透過 Discord 傳送摘要
TODAY=$(date '+%Y-%m-%d')
SUMMARY=$(echo "$OUTPUT" | sed '/SENT_TITLES_START/,/SENT_TITLES_END/d')

if [ -z "$SUMMARY" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 錯誤：claude 沒有輸出內容" >> "$LOG"
  exit 1
fi

if echo "$SUMMARY" | grep -qiE "^Error:|not found in PATH|command not found|Not logged in|Please run /login|Invalid API key|Fix external API key|Insufficient credits|Failed to authenticate|authentication_error|API Error: 401"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 錯誤：claude 回傳錯誤訊息，中止傳送" >> "$LOG"
  echo "$SUMMARY" >> "$LOG"
  exit 1
fi

echo "**論文摘要 ${TODAY}**

${SUMMARY}" | python3 "$BASE/scripts/discord_send.py"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Discord 傳送完成" >> "$LOG"
touch "$BASE/logs/paper_sent_$(date '+%Y%m%d')"

echo "$OUTPUT" >> "$LOG"

# 從輸出中提取新論文標題並寫入 sent_papers.json
NEW_TITLES=$(echo "$OUTPUT" | awk '/SENT_TITLES_START/{found=1; next} /SENT_TITLES_END/{found=0} found && NF')

if [ -n "$NEW_TITLES" ]; then
  python3 - "$SENT_PAPERS_FILE" <<EOF
import json, sys

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

new_titles = """$NEW_TITLES""".strip().split('\n')
new_titles = [t.strip().strip('[]') for t in new_titles if t.strip()]

for t in new_titles:
    if t and t not in data['sent_papers']:
        data['sent_papers'].append(t)

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"已更新 {len(new_titles)} 篇到 sent_papers.json")
EOF
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 執行完成" >> "$LOG"
