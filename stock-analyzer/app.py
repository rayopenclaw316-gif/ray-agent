import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
from utils.sidebar import render_sidebar
from utils.autorefresh import maybe_autorefresh
from data.yf_data import get_index_history

st.set_page_config(
    page_title="台股分析平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
render_sidebar()
maybe_autorefresh()

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
            st.metric(name, f"{latest:,.2f}",
                      f"{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)",
                      delta_color="normal" if chg >= 0 else "inverse")
        elif not df.empty:
            st.metric(name, f"{float(df['Close'].iloc[-1]):,.2f}")
        else:
            st.metric(name, "—")

st.markdown("---")

# ── 類股資金集中分析 ──────────────────────────────────────────
st.subheader("類股資金動向（今日成交量排行）")

@st.cache_data(ttl=600, show_spinner=False)
def _load_sectors():
    SKIP = {"窯製", "加權", "臺灣", "寶島", "發達", "就業", "高薪", "高股息",
            "未含", "小型", "機電", "塑膠化工", "存託"}
    try:
        data = requests.get(
            "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=20
        ).json()
        sectors = []
        for item in data:
            name = item.get("指數", "")
            if "類指數" not in name:
                continue
            if any(k in name for k in SKIP):
                continue
            short = name.replace("類指數", "")
            try:
                pct   = float(item.get("漲跌百分比", 0))
                close = float(item.get("收盤指數", "0").replace(",", ""))
                sign  = item.get("漲跌", "")
                if sign == "-":
                    pct = -abs(pct)
            except Exception:
                pct = 0; close = 0
            sectors.append({"名稱": short, "指數": close, "漲跌%": pct})
        return sorted(sectors, key=lambda x: abs(x["漲跌%"]), reverse=True)
    except Exception:
        return []

sectors = _load_sectors()
if sectors:
    # Top 漲 & 跌
    gainers = [s for s in sectors if s["漲跌%"] > 0][:5]
    losers  = [s for s in sectors if s["漲跌%"] < 0][:5]

    col_g, col_l = st.columns(2)

    with col_g:
        st.markdown("**🔴 漲幅前五名**")
        for s in gainers:
            st.markdown(
                f"**{s['名稱']}** &nbsp; "
                f"<span style='color:#26A65B'>+{s['漲跌%']:.2f}%</span> &nbsp; "
                f"<span style='color:#8b949e'>{s['指數']:,.2f}</span>",
                unsafe_allow_html=True
            )

    with col_l:
        st.markdown("**🟢 跌幅前五名**")
        for s in losers:
            st.markdown(
                f"**{s['名稱']}** &nbsp; "
                f"<span style='color:#E74C3C'>{s['漲跌%']:.2f}%</span> &nbsp; "
                f"<span style='color:#8b949e'>{s['指數']:,.2f}</span>",
                unsafe_allow_html=True
            )

    # 泡泡圖（全類股）
    names   = [s["名稱"] for s in sectors]
    pcts    = [s["漲跌%"] for s in sectors]
    indices = [s["指數"] for s in sectors]
    colors  = ["#26A65B" if p >= 0 else "#E74C3C" for p in pcts]

    fig = go.Figure(go.Bar(
        x=names, y=pcts,
        marker_color=colors,
        text=[f"{p:+.2f}%" for p in pcts],
        textposition="outside",
    ))
    fig.update_layout(
        title="各類股今日漲跌幅",
        template="plotly_dark",
        height=360,
        margin=dict(l=8, r=8, t=44, b=80),
        xaxis_tickangle=-45,
        yaxis_title="漲跌 %",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("類股資料載入中，或今日為非交易日。")

st.markdown("---")

# ── 使用說明 ──────────────────────────────────────────────────
col_l, col_r = st.columns([2, 1])
with col_l:
    st.markdown("### 各頁面說明")
    st.markdown("""
| 頁面 | 內容 |
|------|------|
| **公司總覽** | 股價走勢、K線、配息歷史 |
| **基本面分析** | 財務趨勢、比率、現金流品質、財報警示 |
| **技術分析** | K線＋均線、RSI、MACD、KD |
| **籌碼分析** | 三大法人買賣超、融資融券 |
| **總體經濟** | 美股走勢、VIX、台幣匯率 |
| **產品競爭力** | 公司產品白話說明、競爭優勢、AI 分析 |
| **教育專區** | 所有指標的白話解說與公式 |
""")
with col_r:
    st.info("""
**台股代碼規則**

- TWSE 上市：直接輸入，如 `2330`
- OTC 上櫃：如查無資料，試 `6533.TWO`
- ETF：如 `0050`、`00878`

資料約 15 分鐘延遲。
交易時間內每 10 分鐘自動更新。
""")
