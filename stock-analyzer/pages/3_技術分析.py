import streamlit as st
from utils.sidebar import render_sidebar
from utils.autorefresh import maybe_autorefresh
from data.yf_data import get_price_history
from analysis.technical import add_indicators
from utils.charts import candlestick, volume, rsi, macd, kd

st.set_page_config(page_title="技術分析", page_icon="📉", layout="wide")
render_sidebar()
maybe_autorefresh()
code = st.session_state.get("stock_code", "2330")

st.title(f"📉 技術分析 — {code}")

# ── 參數設定 ──────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    period = st.selectbox("時間範圍", ["3mo","6mo","1y","2y","5y"], index=2,
                           format_func=lambda x: {"3mo":"3個月","6mo":"6個月","1y":"1年","2y":"2年","5y":"5年"}[x])
with c2:
    mas_sel = st.multiselect("均線", ["MA5","MA20","MA60","MA120","MA240"],
                              default=["MA5","MA20","MA60"])
with c3:
    show_bb = st.checkbox("布林通道 (BB)", value=True)

# ── 載入資料 ──────────────────────────────────────────────────
with st.spinner("計算技術指標..."):
    df = get_price_history(code, period)
    df = add_indicators(df)

if df.empty:
    st.error("無法取得股價資料，請確認股票代碼。")
    st.stop()

# ── K線圖 ──────────────────────────────────────────────────
ma_pairs = [(m, m) for m in mas_sel]

import plotly.graph_objects as go
from utils.charts import C, _base

# 主圖（K線 + 均線 + 可選 BB）
fig_candle = go.Figure(go.Candlestick(
    x=df.index,
    open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
    increasing_line_color=C["up"], decreasing_line_color=C["down"],
    name="K線",
))
from utils.charts import MA_COLORS
for i, (col, label) in enumerate(ma_pairs):
    if col in df.columns:
        fig_candle.add_trace(go.Scatter(x=df.index, y=df[col], name=label,
                                         line=dict(color=MA_COLORS[i % 5], width=1.2)))
if show_bb and "BB_upper" in df.columns:
    fig_candle.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB上軌",
                                     line=dict(color="rgba(149,165,166,0.6)", width=1, dash="dash")))
    fig_candle.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB下軌",
                                     line=dict(color="rgba(149,165,166,0.6)", width=1, dash="dash"),
                                     fill="tonexty", fillcolor="rgba(149,165,166,0.06)"))

_base(fig_candle, f"{code} K線圖", 480)
st.plotly_chart(fig_candle, use_container_width=True)
st.plotly_chart(volume(df), use_container_width=True)

# ── 技術指標 ──────────────────────────────────────────────────
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["RSI", "MACD", "KD"])

with tab1:
    st.plotly_chart(rsi(df), use_container_width=True)
    st.markdown("""
**RSI 判讀**
- RSI > 70：超買區，可能面臨回調
- RSI < 30：超賣區，可能出現反彈
- 中樞 50：多空分界線
""")

with tab2:
    st.plotly_chart(macd(df), use_container_width=True)
    st.markdown("""
**MACD 判讀**
- 黃金交叉（MACD 上穿 Signal）：短期動能轉強，買入訊號
- 死亡交叉（MACD 下穿 Signal）：動能轉弱，賣出訊號
- 柱狀體：正值表示 MACD > Signal，動能偏多；負值偏空
""")

with tab3:
    st.plotly_chart(kd(df), use_container_width=True)
    st.markdown("""
**KD 判讀**
- K > 80 且 D > 80：超買，注意賣壓
- K < 20 且 D < 20：超賣，注意買機
- K 上穿 D（黃金交叉）：短線轉強訊號
- K 下穿 D（死亡交叉）：短線轉弱訊號
""")

# ── 最近 20 天資料 ──────────────────────────────────────────────────
with st.expander("最近 20 個交易日數據"):
    cols_show = ["Open","High","Low","Close","Volume"] + \
                [m for m in ["MA5","MA20","MA60"] if m in df.columns] + \
                ["RSI","MACD","K","D"]
    cols_show = [c for c in cols_show if c in df.columns]
    st.dataframe(df[cols_show].tail(20).round(2), use_container_width=True)
