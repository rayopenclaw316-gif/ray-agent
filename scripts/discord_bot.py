#!/usr/bin/env python3
import discord
import asyncio
import os
import glob as glob_module
import time
from dotenv import load_dotenv

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_BASE, '.env'))

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))

CLAUDE_PATH = '/Applications/cmux.app/Contents/Resources/bin/claude'
ALLOWED_TOOLS = ','.join([
    'Bash',
    'Read',
    'Write',
    'Edit',
    'mcp__firecrawl__firecrawl_search',
    'mcp__firecrawl__firecrawl_scrape',
    'mcp__google-workspace__createGmailDraft',
    'mcp__google-workspace__sendGmailDraft',
    'mcp__google-workspace__searchGmail',
    'mcp__google-workspace__readGmailMessage',
    'mcp__google-workspace__createDocument',
    'mcp__google-workspace__createSpreadsheet',
])

PPT_STYLE_RULES = """
=== PPT 製作強制規範（每次都必須遵守）===

必須使用 python-pptx 程式碼製作 PPTX，禁止使用 Google Slides MCP。
輸出路徑：/Users/rayopenclaw/ray-agent/pptx/<檔名>.pptx

【版面規格（單位 cm）】
- 投影片尺寸：33.87 × 19.05 cm
- 標題文字框：left=2.3, top=1.0, width=29.2, height=3.7
- 內容文字框：left=2.3, top=5.1, width=29.2, height=12.1
- 頁碼文字框：left=23.9, top=17.7, width=3.0, height=1.0

【視覺風格】
- 背景：純白，prs.slide_layouts[6]（blank layout），不加任何填色
- 無裝飾元素：不加色塊 header bar、底部線條、圖示裝飾、emoji
- 標題顏色：#0E2841，粗體，Times New Roman，28–30 pt
- 內文顏色：黑色，Times New Roman，17–18 pt
- 技術術語一律標紅 #FF0000：EMG, EEG, sEMG, SNN, CNN, 1D-CNN, BLE, SSR, SSI, Siamese, Transformer, GRU, LSTM, Few-shot, Trigram, Moving Window, PMLSF, Sensor Fusion, Language Model, CDAN, MMD, Domain Adaptation
- 字型：每個 run 的 latin/ea/cs 三個 xml 標籤都設定（英文 Times New Roman、中文 標楷體）

【程式碼慣例】
- _set_fonts(run, font_name) 設定 latin/ea/cs 三個 xml 字型標籤
- _split_lang(text) 將字串拆成中文/英文片段
- add_text(para, text, ...) 處理混合語言 + 紅色術語高亮

【必要內容結構】
1. 封面：中英文並列標題（英文原標題 + 中文翻譯）+ 期刊名 + 作者群 + 日期
2. 目錄頁：每章節右側標明對應頁碼
3. 核心技術要有獨立投影片說明原理（內容充實，不能過少）
4. 必須包含圖片（架構圖、流程圖等）；無法取得原圖時用矩形+箭頭組合繪製示意圖

【資料來源與內容深度（嚴格遵守）】
- 必須嚴格按照 PDF 或網頁原文全文撰寫，不得僅憑摘要概括
- 必須包含：資料集細節（受試者數、詞彙數、session 數）、模型架構細節（層數、kernel size、feature 維度）、與其他方法的比較表
- 所有專有名詞必須解釋清楚：定義 + 原理 + 在本論文中的角色
- 公式必須完整呈現且每個符號都要解釋，不得截斷
- 若原文資料不足，可主動搜尋補充資料，但必須與原論文比對確認正確後才放入 PPT
=== 規範結束 ===
"""

import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, 'discord_sessions.json')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
_ready_sent = False


def load_sessions() -> dict:
    try:
        with open(SESSION_FILE) as f:
            return {int(k): v for k, v in json.load(f).items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_sessions(sessions: dict):
    with open(SESSION_FILE, 'w') as f:
        json.dump({str(k): v for k, v in sessions.items()}, f, indent=2)


# channel_id -> session_id（持久化至磁碟）
channel_sessions: dict[int, str] = load_sessions()


PPT_KEYWORDS = ('ppt', 'pptx', '簡報', '投影片', 'presentation', 'slide')

def is_ppt_request(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in PPT_KEYWORDS)

def get_new_pptx_files(before_snapshot: dict) -> list[str]:
    output_dir = '/Users/rayopenclaw/ray-agent/pptx'
    found = []
    for path in glob_module.glob(os.path.join(output_dir, '*.pptx')):
        mtime = os.path.getmtime(path)
        if path not in before_snapshot or before_snapshot[path] < mtime:
            found.append(path)
    return found

def snapshot_pptx() -> dict:
    output_dir = '/Users/rayopenclaw/ray-agent/pptx'
    result = {}
    for path in glob_module.glob(os.path.join(output_dir, '*.pptx')):
        result[path] = os.path.getmtime(path)
    return result

async def run_claude(prompt: str, channel_id: int) -> tuple[str, list[str]]:
    env = {
        **os.environ,
        'PATH': '/Applications/cmux.app/Contents/Resources/bin:/Users/rayopenclaw/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
        'HOME': '/Users/rayopenclaw',
        'USER': 'rayopenclaw',
    }

    if is_ppt_request(prompt):
        full_prompt = PPT_STYLE_RULES + '\n\n使用者指令：' + prompt
    else:
        full_prompt = prompt

    before = snapshot_pptx()

    session_id = channel_sessions.get(channel_id)
    cmd = [CLAUDE_PATH, '-p', full_prompt, '--allowedTools', ALLOWED_TOOLS, '--output-format', 'json']
    if session_id:
        cmd += ['--resume', session_id]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd='/Users/rayopenclaw/ray-agent',
    )
    stdout, stderr = await proc.communicate()
    raw = stdout.decode('utf-8').strip()

    new_files = get_new_pptx_files(before)

    if not raw:
        return stderr.decode('utf-8').strip() or '（無回應）', new_files

    try:
        data = json.loads(raw)
        if sid := data.get('session_id'):
            channel_sessions[channel_id] = sid
            save_sessions(channel_sessions)
        text = data.get('result') or data.get('content') or raw
        return text, new_files
    except json.JSONDecodeError:
        return raw, new_files


async def send_long(channel, text: str):
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    for chunk in chunks:
        await channel.send(chunk)
        await asyncio.sleep(0.3)


@client.event
async def on_ready():
    global _ready_sent
    print(f'Bot 已上線：{client.user}')
    if _ready_sent:
        return
    _ready_sent = True
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('RayResearchBot 已上線，可以開始下指令。')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != CHANNEL_ID:
        return

    user_input = message.content.strip()
    if not user_input:
        return

    if user_input.lower() == '!reset':
        channel_sessions.pop(message.channel.id, None)
        save_sessions(channel_sessions)
        await message.channel.send('對話記憶已清除，下一則訊息將開始全新對話。')
        return

    async with message.channel.typing():
        response, new_pptx_files = await run_claude(user_input, message.channel.id)

    await send_long(message.channel, response)

    for pptx_path in new_pptx_files:
        fname = os.path.basename(pptx_path)
        await message.channel.send(
            f'📎 PPT 已產生：`{fname}`',
            file=discord.File(pptx_path, filename=fname)
        )


client.run(TOKEN)
