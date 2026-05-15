#!/bin/bash
# Claude Code Stop hook：Discord 通知 + git 同步
cat > /dev/null  # 丟棄 stdin (stop event JSON)

REPO="/Users/rayopenclaw/ray-agent"

printf "🤖 Claude Code 對話結束\n時間：$(date '+%Y-%m-%d %H:%M')" \
  | python3 "$REPO/scripts/discord_send.py" 2>/dev/null &

bash "$REPO/scripts/auto_sync.sh" 2>/dev/null &
