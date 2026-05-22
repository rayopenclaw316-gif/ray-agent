import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.sidebar import render_sidebar
from data.yf_data import get_index_history
from utils.charts import C, _base

st.set_page_config(page_title="總體經濟", page_icon="🌐", layout="wide")
render_sidebar()

st.title("🌐 總體經濟環境")
st.caption("美股走勢、波動度、利率、匯率。台股與美股高度連動，這些是看盤前的重要背景。")

PERIOD_OPT = ["3mo","6mo","1y","2y"]
period = st.radio("時間範圍", PERIOD_OPT, index=2, horizontal=True,
                   format_func=lambda x: {"3mo":"3個月","6mo":"6個月","1y":"1年","2y":"2年"}[x])

# ── 美股三大指數 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("美股三大指數 vs 台股加權指數")

INDICES = {
    "台股加權 (^TWII)": "^TWII",
    "S&P 500 (^GSPC)":  "^GSPC",
    "NASDAQ (^IXIC)":   "^IXIC",
    "道瓊 (^DJI)":       "^DJI",
}

with st.spinner("載入指數資料..."):
    idx_data = {name: get_index_history(sym, period) for name, sym in INDICES.items()}

# Quick metrics
cols = st.columns(4)
for i, (name, sym) in enumerate(INDICES.items()):
    df = idx_data[name]
    with cols[i]:
        if not df.empty and len(df) >= 2:
            latest = float(df["Close"].iloc[-1])
            prev   = float(df["Close"].iloc[-2])
            chg    = latest - prev
            chg_p  = chg / prev * 100
            sign   = "+" if chg >= 0 else ""
            st.metric(name.split("(")[0].strip(), f"{latest:,.2f}",
                      f"{sign}{chg:.2f} ({sign}{chg_p:.2f}%)",
                      delta_color="normal" if chg >= 0 else "inverse")
        else:
            st.metric(name, "—")

# Normalised comparison chart
fig = go.Figure()
clrs = [C["orange"], C["blue"], C["teal"], C["purple"]]
for i, (name, df) in enumerate(idx_data.items()):
    if df.empty:
        continue
    base = float(df["Close"].iloc[0])
    norm = (df["Close"] / base - 1) * 100
    fig.add_trace(go.Scatter(
        x=df.index, y=norm, name=name.split("(")[0].strip(),
        line=dict(color=clrs[i % 4], width=2),
    ))
fig.update_layout(title="相對報酬（基準期間起漲跌 %）",
                   yaxis_title="%", template="plotly_dark", height=360,
                   margin=dict(l=8,r=8,t=40,b=8))
st.plotly_chart(fig, use_container_width=True)

# ── VIX 恐慌指數 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("VIX 恐慌指數")
with st.spinner("載入 VIX..."):
    df_vix = get_index_history("^VIX", period)

if not df_vix.empty:
    fig_vix = go.Figure()
    fig_vix.add_hrect(y0=30, y1=df_vix["Close"].max()+5, fillcolor="red",   opacity=0.05, line_width=0)
    fig_vix.add_hrect(y0=0,  y1=20,                       fillcolor="green", opacity=0.05, line_width=0)
    fig_vix.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5, annotation_text="20 低恐慌")
    fig_vix.add_hline(y=30, line_dash="dash", line_color="red",   opacity=0.5, annotation_text="30 高恐慌")
    fig_vix.add_trace(go.Scatter(x=df_vix.index, y=df_vix["Close"],
                                  fill="tozeroy", fillcolor="rgba(231,76,60,0.15)",
                                  line=dict(color=C["down"], width=1.5), name="VIX"))
    _base(fig_vix, "VIX 恐慌指數", 300)
    st.plotly_chart(fig_vix, use_container_width=True)
    latest_vix = float(df_vix["Close"].iloc[-1])
    if latest_vix < 20:
        st.success(f"VIX = {latest_vix:.1f}｜市場平靜，投資人情緒穩定")
    elif latest_vix < 30:
        st.warning(f"VIX = {latest_vix:.1f}｜波動升溫，需留意風險")
    else:
        st.error(f"VIX = {latest_vix:.1f}｜恐慌區間，市場波動劇烈")

# ── 美元指數 & 台幣匯率 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("匯率 & 美債利率")
c1, c2 = st.columns(2)

with c1:
    st.markdown("**USD/TWD 台幣匯率**")
    df_twd = get_index_history("TWD=X", period)
    if not df_twd.empty:
        fig2 = go.Figure(go.Scatter(x=df_twd.index, y=df_twd["Close"],
                                     fill="tozeroy", line=dict(color=C["teal"], width=1.5), name="USD/TWD"))
        _base(fig2, "美元兌台幣（USD/TWD）", 280)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("匯率上升（台幣貶值）→ 出口商受益（如台積電、鴻海），進口商成本上升。")

with c2:
    st.markdown("**美國 10 年期公債殖利率**")
    df_tnx = get_index_history("^TNX", period)
    if not df_tnx.empty:
        fig3 = go.Figure(go.Scatter(x=df_tnx.index, y=df_tnx["Close"],
                                     fill="tozeroy", line=dict(color=C["orange"], width=1.5), name="10Y Treasury"))
        _base(fig3, "美國 10Y 公債殖利率（%）", 280)
        st.plotly_chart(fig3, use_container_width=True)
        latest_tnx = float(df_tnx["Close"].iloc[-1])
        st.caption(f"當前利率：{latest_tnx:.2f}%。利率升高 → 高 P/E 成長股壓力加大，金融股受益。")
