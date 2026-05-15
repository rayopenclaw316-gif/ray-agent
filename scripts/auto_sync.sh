#!/bin/bash
REPO="/Users/rayopenclaw/ray-agent"
LOG="$REPO/logs/auto_sync.log"

mkdir -p "$REPO/logs"

cd "$REPO" || exit 1

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "$(date '+%Y-%m-%d %H:%M') no changes" >> "$LOG"
  exit 0
fi

git add .
git commit -m "auto sync: $(date '+%Y-%m-%d %H:%M')"
git push origin main >> "$LOG" 2>&1
echo "$(date '+%Y-%m-%d %H:%M') synced" >> "$LOG"
