#!/usr/bin/env python3
"""從 stdin 讀取文字，分段傳送到 Discord 頻道"""
import sys
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_base, '.env'))

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
API_URL = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages'

def send(text: str) -> bool:
    payload = json.dumps({'content': text}).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            'Authorization': f'Bot {TOKEN}',
            'Content-Type': 'application/json',
            'User-Agent': 'DiscordBot (https://github.com/rayopenclaw, 1.0)',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status < 300
    except urllib.error.HTTPError as e:
        print(f'Discord 傳送失敗：{e.code} {e.read().decode()}', file=sys.stderr)
        return False
    except Exception as e:
        print(f'Discord 傳送失敗：{e}', file=sys.stderr)
        return False

def send_long(text: str, chunk_size: int = 1900) -> bool:
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    ok = True
    for chunk in chunks:
        if not send(chunk):
            ok = False
    return ok

if __name__ == '__main__':
    content = sys.stdin.read().strip()
    if content:
        success = send_long(content)
        sys.exit(0 if success else 1)
