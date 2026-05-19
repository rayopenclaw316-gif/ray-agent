#!/bin/bash
# 每日科技探索推播 - 台灣時間 15:35 自動執行

export PATH="/Applications/cmux.app/Contents/Resources/bin:/Users/rayopenclaw/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/Users/rayopenclaw"

LOG="/Users/rayopenclaw/ray-agent/logs/tech_digest.log"
mkdir -p "$(dirname "$LOG")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 腳本啟動" >> "$LOG"

# HOME 已設定，claude CLI 會自動從 Keychain 讀取 OAuth 憑證並處理 token 刷新
# 不設 ANTHROPIC_API_KEY，避免短期 accessToken 過期導致 401

BASE="/Users/rayopenclaw/ray-agent"
SENT_TOPICS_FILE="$BASE/sent_topics.json"

# 防止同一天重複執行
SENT_FLAG="$BASE/logs/tech_sent_$(date '+%Y%m%d')"
if [ -f "$SENT_FLAG" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 今日已送出，略過" >> "$LOG"
  exit 0
fi

SENT_LIST=$(python3 -c "import json; d=json.load(open('$SENT_TOPICS_FILE')); print('\n'.join(d['sent_articles']))" 2>/dev/null || echo "（無記錄）")

PROMPT="你是陳睿莆的技術探索助理。今天請為他精選一則深度技術內容。

## 你的任務
從以下類別中隨機挑一個方向：
1. **GitHub 熱門專案**：近期爆紅的開源工具、即時換臉、AI 生成、自動化工具等
2. **商業技術趨勢**：新創公司採用的技術手法、SaaS 產品架構、scalability 策略
3. **產品設計與製作流程**：軟硬體產品從概念到上市的流程、設計思維、快速驗證方法
4. **跨領域 AI 應用**：AI 在醫療、農業、藝術、教育、遊戲等非傳統領域的突破
5. **通訊與協定技術**：Modbus、MQTT、BLE、WebSocket、gRPC 等工業或物聯網協定的實際應用
6. **製造與硬體技術**：3D 列印新材料、MEMS 感測器、PCB 設計技巧、嵌入式系統創新

**重要：以下文章或連結已曾推播過，不得使用相同來源，但同主題的其他文章或更深入的面向仍可探討：**
$SENT_LIST

## 內容深度要求（重要）
不要只是表面介紹，要達到以下深度：
- **技術原理**：說明核心機制是如何運作的，不只是「它能做什麼」
- **實作細節**：關鍵的設計決策、架構選擇、或演算法邏輯
- **優缺點分析**：與現有方案的比較，這個技術在哪些場景會失效
- **實際數據或案例**：有具體的效能數字、使用規模、或真實部署案例
- **可以動手試的切入點**：如果讀者想實際玩看看，從哪裡開始

## 輸出格式（繁體中文，600～900 字）

**今日科技探索 🔍**
**主題**：[一句話標題]
**類別**：[上方類別名稱]

---

[深度正文，涵蓋上述五個面向]

---
**和你的研究可能的連結**：[若與 sEMG、義肢控制、無聲語音介面、深度學習有關聯則說明；無關聯直接省略此段]
**延伸關鍵字**：[3～5 個搜尋關鍵字]
**參考來源**：[連結]

在內容最後加上以下區塊（系統記錄用，不顯示給使用者）：
SENT_ARTICLE_START
[本次參考的主要文章或連結 URL，附上日期，格式：URL (YYYY-MM-DD)]
SENT_ARTICLE_END

## 規則
- 使用 WebSearch 搜尋，找到文章後用 WebFetch 爬取內文，確保掌握足夠細節
- 內容必須是近一年內的
- 全程繁體中文，技術術語附英文原文"

OUTPUT=$( /Applications/cmux.app/Contents/Resources/bin/claude -p "$PROMPT" \
  --allowedTools "WebSearch,WebFetch" \
  --output-format text \
  --dangerously-skip-permissions 2>&1 )

TODAY=$(date '+%Y-%m-%d')

if [ -z "$OUTPUT" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 錯誤：claude 沒有輸出內容" >> "$LOG"
  exit 1
fi

if echo "$OUTPUT" | grep -qiE "^Error:|not found in PATH|command not found|Not logged in|Please run /login|Invalid API key|Fix external API key|Insufficient credits|Failed to authenticate|authentication_error|API Error: 401"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 錯誤：claude 回傳錯誤訊息，中止傳送" >> "$LOG"
  echo "$OUTPUT" >> "$LOG"
  exit 1
fi

# 移除記錄區塊後送出
CONTENT=$(echo "$OUTPUT" | sed '/SENT_ARTICLE_START/,/SENT_ARTICLE_END/d')

echo "**📡 每日科技探索 ${TODAY}**

${CONTENT}" | python3 "$BASE/scripts/discord_send.py"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Discord 傳送完成" >> "$LOG"
touch "$BASE/logs/tech_sent_$(date '+%Y%m%d')"

# 提取文章連結並寫入 sent_topics.json
NEW_ARTICLE=$(echo "$OUTPUT" | awk '/SENT_ARTICLE_START/{found=1; next} /SENT_ARTICLE_END/{found=0} found && NF')

if [ -n "$NEW_ARTICLE" ]; then
  python3 - "$SENT_TOPICS_FILE" <<EOF
import json, sys
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)
article = """$NEW_ARTICLE""".strip().strip('[]')
if article and article not in data['sent_articles']:
    data['sent_articles'].append(article)
with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"已記錄文章：{article}")
EOF
fi

echo "$OUTPUT" >> "$LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 執行完成" >> "$LOG"
