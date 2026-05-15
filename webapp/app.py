#!/usr/bin/env python3
import os, json, time, requests
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

FIRECRAWL_KEY = 'fc-0eeba87cf95b4d04a1be8014ccc0abe9'
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
FIRECRAWL_URL = 'https://api.firecrawl.dev/v1/search'
ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages'
TWSE_OPEN     = 'https://openapi.twse.com.tw/v1'

_cache = {}

def cached(key, ttl, fn):
    now = time.time()
    if key in _cache and now - _cache[key]['t'] < ttl:
        return _cache[key]['v']
    val = fn()
    _cache[key] = {'t': now, 'v': val}
    return val

# ── 產業別代碼對照 ──────────────────────────────────────────
SECTOR_MAP = {
    '01': '水泥工業', '02': '食品工業', '03': '塑膠工業',
    '04': '紡織纖維', '05': '電機機械', '06': '電器電纜',
    '07': '化學工業', '08': '玻璃陶瓷', '09': '造紙工業',
    '10': '鋼鐵工業', '11': '橡膠工業', '12': '汽車工業',
    '13': '電子工業', '14': '建材營造', '15': '航運業',
    '16': '觀光餐旅', '17': '金融保險', '18': '貿易百貨',
    '19': '綜合', '20': '其他', '21': '化學生技醫療',
    '22': '半導體業', '23': '電腦及週邊設備業',
    '24': '光電業', '25': '通信網路業', '26': '電子零組件業',
    '27': '電子通路業', '28': '資訊服務業', '29': '其他電子業',
    '31': '存託憑證',
}

# ── 主要產業顏色 ──
SECTOR_COLOR = {
    '半導體業': '#f97316', '電腦及週邊設備業': '#3b82f6',
    '電子工業': '#8b5cf6', '電子零組件業': '#06b6d4',
    '金融保險': '#10b981', '光電業': '#eab308',
    '通信網路業': '#ec4899', '化學生技醫療': '#14b8a6',
    '航運業': '#64748b', '鋼鐵工業': '#a16207',
}


# ── TWSE OpenAPI ──────────────────────────────────────────────
def fetch_all_stocks():
    def _fetch():
        r = requests.get(f'{TWSE_OPEN}/exchangeReport/STOCK_DAY_ALL',
                         headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        return r.json()
    return cached('all_stocks', 180, _fetch)


def fetch_sector_map():
    """回傳 {股票代號: 產業別原始代碼} """
    def _fetch():
        r = requests.get(f'{TWSE_OPEN}/opendata/t187ap03_L',
                         headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        return {item.get('公司代號', '').strip(): item.get('產業別', '').strip()
                for item in r.json()}
    return cached('sector_map', 3600, _fetch)


def get_sectors():
    """各類股指數漲跌 + 估算成交金額"""
    def _fetch():
        # 取 MI_INDEX 各類指數（含 漲跌百分比）
        r = requests.get(f'{TWSE_OPEN}/exchangeReport/MI_INDEX',
                         headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        index_data = r.json()
        # 過濾出 X類指數（排除複合型）
        SKIP = {'窯製', '加權', '臺灣', '寶島', '發達', '就業', '高薪', '高股息',
                '未含', '小型', '機電', '塑膠化工'}
        sectors = []
        for item in index_data:
            name = item.get('指數', '')
            if '類指數' not in name:
                continue
            if any(k in name for k in SKIP):
                continue
            short = name.replace('類指數', '')
            try:
                pct = float(item.get('漲跌百分比', '0'))
                close = float(item.get('收盤指數', '0').replace(',', ''))
            except Exception:
                pct = 0; close = 0
            sectors.append({
                'name':       short,
                'index':      close,
                'change_pct': pct,
                'color':      SECTOR_COLOR.get(short, '#4b5563'),
            })

        # 加上各類成交金額（從 STOCK_DAY_ALL 彙整）
        # 產業別代碼 → MI_INDEX 短名稱（精確對應）
        CODE_TO_SECTOR = {
            '01':'水泥', '02':'食品', '03':'塑膠', '04':'紡織纖維',
            '05':'電機機械', '06':'電器電纜', '07':'化學', '08':'玻璃陶瓷',
            '09':'造紙', '10':'鋼鐵', '11':'橡膠', '12':'汽車',
            '14':'建材營造', '15':'航運', '16':'觀光餐旅', '17':'金融保險',
            '18':'貿易百貨', '19':'綜合', '20':'其他', '21':'化學生技醫療',
            '22':'生技醫療', '23':'油電燃氣', '24':'半導體',
            '25':'電腦及週邊設備', '26':'光電', '27':'通信網路',
            '28':'電子零組件', '29':'電子通路', '30':'資訊服務',
            '31':'其他電子', '35':'綠能環保', '36':'運動休閒',
        }
        sec_map = fetch_sector_map()
        stocks_raw = fetch_all_stocks()
        vol_bucket = {}
        for s in stocks_raw:
            code = s.get('Code', '').strip()
            raw_sec_code = sec_map.get(code, '')
            sec_name = CODE_TO_SECTOR.get(raw_sec_code, '其他')
            try:
                val = int(s.get('TradeValue', '0') or '0')
            except Exception:
                val = 0
            vol_bucket[sec_name] = vol_bucket.get(sec_name, 0) + val

        for s in sectors:
            name = s['name']  # e.g. '半導體', '光電', '金融保險'
            s['value_b'] = round(vol_bucket.get(name, 0) / 1e8, 1)

        sectors.sort(key=lambda x: abs(x['change_pct']), reverse=True)
        return sectors
    return cached('sectors', 180, _fetch)


def get_top_stocks(n=30):
    """成交金額前 N 名個股"""
    def _fetch():
        stocks = fetch_all_stocks()
        sec_map = fetch_sector_map()
        rows = []
        for s in stocks:
            try:
                val = int(s.get('TradeValue', '0') or '0')
                vol = int(s.get('TradeVolume', '0') or '0')
                chg = float(s.get('Change', '0') or '0')
                close = float(s.get('ClosingPrice', '0') or '0')
                prev = close - chg if close else 0
                chg_pct = round(chg / prev * 100, 2) if prev else 0
            except Exception:
                val = vol = 0; chg = chg_pct = 0; close = 0
            code = s.get('Code', '').strip()
            rows.append({
                'code':     code,
                'name':     s.get('Name', '').strip(),
                'close':    s.get('ClosingPrice', ''),
                'change':   s.get('Change', ''),
                'change_pct': chg_pct,
                'volume':   vol,
                'value_b':  round(val / 1e8, 2),
                'sector':   sec_map.get(code, ''),
            })
        rows.sort(key=lambda x: x['value_b'], reverse=True)
        return rows[:n]
    return cached('top_stocks', 180, _fetch)


def get_institutional():
    """三大法人"""
    def _fetch():
        r = requests.get(f'{TWSE_OPEN}/fund/BFI82U',
                         headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        data = r.json()
        result = []
        for item in data:
            net = item.get('BuyOrSell', item.get('買賣差額', '0')).replace(',', '').replace('+', '')
            result.append({
                'type': item.get('Name', item.get('單位名稱', '')),
                'buy':  item.get('Buy', item.get('買進金額', '0')).replace(',', ''),
                'sell': item.get('Sell', item.get('賣出金額', '0')).replace(',', ''),
                'net':  net,
            })
        return result
    return cached('institutional', 300, _fetch)


def get_stock_price(code):
    """個股資料 via yfinance"""
    def _fetch():
        try:
            t = yf.Ticker(f'{code}.TW')
            info = t.fast_info
            hist = t.history(period='2d')
            if hist.empty:
                return {}
            last  = hist.iloc[-1]
            prev  = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
            chg   = round(last['Close'] - prev['Close'], 2)
            chg_p = round(chg / prev['Close'] * 100, 2) if prev['Close'] else 0
            return {
                'code':      code,
                'close':     round(last['Close'], 2),
                'open':      round(last['Open'], 2),
                'high':      round(last['High'], 2),
                'low':       round(last['Low'], 2),
                'volume':    int(last['Volume']),
                'change':    chg,
                'change_pct': chg_p,
                'market_cap': getattr(info, 'market_cap', 0),
                'date':      str(hist.index[-1])[:10],
            }
        except Exception as e:
            return {'error': str(e)}
    return cached(f'price_{code}', 120, _fetch)


# ── Firecrawl 搜尋 ──────────────────────────────────────────
def fc_search(query, limit=8, lang='zh', country='tw'):
    try:
        r = requests.post(
            FIRECRAWL_URL,
            headers={'Authorization': f'Bearer {FIRECRAWL_KEY}',
                     'Content-Type': 'application/json'},
            json={'query': query, 'limit': limit, 'lang': lang,
                  'country': country},
            timeout=25,
        )
        results = []
        for item in r.json().get('data', []):
            results.append({
                'title':   item.get('title', ''),
                'url':     item.get('url', ''),
                'snippet': item.get('description', ''),
                'source':  item.get('url', '').split('/')[2] if item.get('url') else '',
            })
        return results
    except Exception as e:
        return []


# ── Claude API ──────────────────────────────────────────────
def claude(prompt, max_tokens=600):
    if not ANTHROPIC_KEY:
        return '（未設定 ANTHROPIC_API_KEY）'
    try:
        r = requests.post(
            ANTHROPIC_URL,
            headers={'x-api-key': ANTHROPIC_KEY,
                     'anthropic-version': '2023-06-01',
                     'Content-Type': 'application/json'},
            json={'model': 'claude-haiku-4-5-20251001',
                  'max_tokens': max_tokens,
                  'messages': [{'role': 'user', 'content': prompt}]},
            timeout=35,
        )
        return r.json()['content'][0]['text']
    except Exception as e:
        return f'AI 分析失敗：{e}'


# ── Routes ──────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sectors')
def api_sectors():
    return jsonify(get_sectors())

@app.route('/api/top-stocks')
def api_top_stocks():
    return jsonify(get_top_stocks())

@app.route('/api/institutional')
def api_institutional():
    try:
        return jsonify(get_institutional())
    except Exception as e:
        return jsonify([])

@app.route('/api/market-pulse')
def api_market_pulse():
    def _fetch():
        today = datetime.now().strftime('%Y年%m月%d日')
        tw = fc_search(f'台股 類股 資金 {today}', limit=6)
        us = fc_search(f'US stock Taiwan semiconductor geopolitical impact {today}',
                       limit=6, lang='en', country='us')
        tw_text = '\n'.join(f"- {n['title']}: {n['snippet']}" for n in tw[:6])
        us_text = '\n'.join(f"- {n['title']}: {n['snippet']}" for n in us[:6])
        prompt = f"""你是台股策略分析師，今天是{today}。根據以下國內外最新新聞，用繁體中文分析：
1. 哪些產業類股受到地緣政治或美股走勢的正面/負面影響？（請具體提到半導體、AI、航運等）
2. 今日台股盤面的重點方向與值得關注的族群？
3. 有哪些重要時事（貿易戰、關稅、地緣政治）正在影響台股趨勢？

台灣財經新聞：
{tw_text}

國際新聞：
{us_text}

條列式，每點 1–2 句，總字數 300 字內。"""
        analysis = claude(prompt, max_tokens=500)
        return {'tw_news': tw, 'us_news': us, 'analysis': analysis,
                'updated': datetime.now().strftime('%H:%M:%S')}
    return jsonify(cached('market_pulse', 300, _fetch))

@app.route('/api/stock/<code>')
def api_stock(code):
    return jsonify(get_stock_price(code))

@app.route('/api/stock/<code>/news')
def api_stock_news(code):
    name = request.args.get('name', code)
    def _fetch():
        tw = fc_search(f'{name} {code} 台股 新聞 營收 接單', limit=8)
        en = fc_search(f'{name} Taiwan stock news earnings', limit=4, lang='en', country='us')
        return {'tw': tw, 'en': en}
    return jsonify(cached(f'news_{code}', 300, _fetch))

@app.route('/api/stock/<code>/analysis')
def api_stock_analysis(code):
    name = request.args.get('name', code)
    news = fc_search(f'{name} {code} 接單 合約 法說 營收 未來展望 大客戶', limit=10)
    news += fc_search(f'{name} {code} Taiwan orders revenue outlook', limit=5, lang='en')
    news_text = '\n'.join(f"- {n['title']}: {n['snippet']}" for n in news[:12])
    prompt = f"""你是台股分析師。根據以下「{name}（{code}）」的最新新聞，用繁體中文整理：
1. 近期重要動態（接單、合作案、法說重點、大客戶動向）
2. 未來發展方向與潛在機會
3. 主要風險與挑戰
4. 短期股價影響評估（一句話）

新聞：
{news_text}

條列式，每點不超過 2 句，總字數 350 字內。"""
    analysis = claude(prompt, max_tokens=700)
    return jsonify({'analysis': analysis, 'sources': len(news)})


if __name__ == '__main__':
    print('🚀 台股資金流向儀表板啟動中...')
    print('📊 請開啟瀏覽器：http://localhost:5001')
    app.run(debug=False, port=5001, host='0.0.0.0')
