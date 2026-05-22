import streamlit as st
from datetime import datetime
from utils.sidebar import render_sidebar
from data.yf_data import get_index_history

st.set_page_config(
    page_title="台股分析平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar()

st.title("📈 台股分析平台")
st.caption(f"本地時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ── 市場概況 ──────────────────────────────────────────────────
st.subheader("市場概況")

INDICES = [
    ("台股加權指數", "^TWII"),
    ("S&P 500",     "^GSPC"),
    ("NASDAQ",      "^IXIC"),
    ("VIX 恐慌指數", "^VIX"),
]

cols = st.columns(4)
for i, (name, sym) in enumerate(INDICES):
    df = get_index_history(sym, "5d")
    with cols[i]:
        if not df.empty and len(df) >= 2:
            latest  = float(df["Close"].iloc[-1])
            prev    = float(df["Close"].iloc[-2])
            chg     = latest - prev
            chg_pct = chg / prev * 100
            sign    = "+" if chg >= 0 else ""
            color   = "normal" if chg >= 0 else "inverse"
            st.metric(name, f"{latest:,.2f}", f"{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)",
                      delta_color=color)
        elif not df.empty:
            st.metric(name, f"{float(df['Close'].iloc[-1]):,.2f}")
        else:
            st.metric(name, "—", "資料暫不可用")

st.markdown("---")

# ── 使用說明 ──────────────────────────────────────────────────
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("使用方式")
    st.markdown("""
1. 在左側輸入**股票代碼**（例：`2330`、`0050`），或點熱門快速切換
2. 切換上方**頁面**進行各面向分析
""")

    st.markdown("### 各頁面說明")
    st.markdown("""
| 頁面 | 內容 |
|------|------|
| **公司總覽** | 股價走勢圖、K線、配息歷史 |
| **基本面分析** | 財務趨勢、財務比率、現金流品質、財報警示 |
| **技術分析** | K線＋均線、RSI、MACD、KD 指標 |
| **籌碼分析** | 三大法人買賣超、融資融券 |
| **總體經濟** | 美股走勢、VIX、台幣匯率 |
| **教育專區** | 所有指標的白話解說、公式、判讀標準 |
""")

with col_r:
    st.subheader("注意事項")
    st.info("""
**台股代碼規則**

- TWSE（上市）：直接輸入代碼，例 `2330`
- OTC（上櫃）：若查無資料，嘗試加 `.TWO`，例 `6533.TWO`
- ETF：直接輸入，例 `0050`、`00878`

資料來源為 Yahoo Finance，具約 15 分鐘延遲。
財務報表資料每日更新一次。
""")
