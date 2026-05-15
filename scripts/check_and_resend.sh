#!/bin/bash
# 每天 17:00 檢查今日推播是否成功，若未成功則補發

export PATH="/Applications/cmux.app/Contents/Resources/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/Users/rayopenclaw"

BASE="/Users/rayopenclaw/ray-agent"
LOG="$BASE/logs/check_resend.log"
TODAY=$(date '+%Y%m%d')

mkdir -p "$BASE/logs"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始檢查" >> "$LOG"

PAPER_FLAG="$BASE/logs/paper_sent_${TODAY}"
TECH_FLAG="$BASE/logs/tech_sent_${TODAY}"

if [ -f "$PAPER_FLAG" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 論文推播：已成功，略過" >> "$LOG"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 論文推播：未發送，補發中..." >> "$LOG"
  bash "$BASE/scripts/daily_paper_search.sh"
  if [ -f "$PAPER_FLAG" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 論文推播：補發成功" >> "$LOG"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 論文推播：補發失敗，請手動確認" >> "$LOG"
  fi
fi

if [ -f "$TECH_FLAG" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 科技探索：已成功，略過" >> "$LOG"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 科技探索：未發送，補發中..." >> "$LOG"
  bash "$BASE/scripts/daily_tech_digest.sh"
  if [ -f "$TECH_FLAG" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 科技探索：補發成功" >> "$LOG"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 科技探索：補發失敗，請手動確認" >> "$LOG"
  fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 檢查完成" >> "$LOG"
