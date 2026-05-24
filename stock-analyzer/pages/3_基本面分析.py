import streamlit as st
import pandas as pd
from utils.sidebar import render_sidebar
from data.yf_data import get_stock_info, get_financials
from analysis.fundamental import get_ratio_table, get_income_trend, cashflow_quality
from analysis.fraud import check_signals
from utils.charts import line_multi, bar_signed

st.set_page_config(page_title="基本面分析", page_icon="📊", layout="wide")
render_sidebar()
code = st.session_state.get("stock_code", "2330")

st.title(f"📊 基本面分析 — {code}")

with st.spinner("載入財務資料..."):
    info = get_stock_info(code)
    fins = get_financials(code)

income   = fins.get("income",   pd.DataFrame())
cashflow = fins.get("cashflow", pd.DataFrame())
balance  = fins.get("balance",  pd.DataFrame())

# ── 財務比率 ──────────────────────────────────────────────────
st.subheader("財務比率一覽")
ratio_df = get_ratio_table(info)
if ratio_df.empty:
    st.info("無法取得財務比率（Yahoo Finance 對部分台股資料有限）。")
else:
    half = len(ratio_df) // 2 + len(ratio_df) % 2
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(ratio_df.iloc[:half].set_index("指標"), use_container_width=True)
    with c2:
        st.dataframe(ratio_df.iloc[half:].set_index("指標"), use_container_width=True)

# ── P/E 估值評估 ──────────────────────────────────────────────
pe = info.get("trailingPE")
if pe:
    st.markdown("---")
    st.subheader("估值快速評估")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**P/E 本益比**")
        if pe < 10:
            st.success(f"P/E = {pe:.1f}｜偏低（可能低估，或市場擔憂成長性）")
        elif pe < 20:
            st.success(f"P/E = {pe:.1f}｜合理區間")
        elif pe < 30:
            st.warning(f"P/E = {pe:.1f}｜偏高（需要高成長支撐）")
        elif pe < 50:
            st.error(f"P/E = {pe:.1f}｜昂貴（高成長預期中）")
        else:
            st.error(f"P/E = {pe:.1f}｜極度昂貴（高風險）")
    with c2:
        pb = info.get("priceToBook")
        roe = info.get("returnOnEquity")
        if pb:
            st.markdown("**P/B 股價淨值比**")
            if pb < 1:
                st.warning(f"P/B = {pb:.2f}｜低於帳面價值（留意是否有隱患）")
            elif pb < 3:
                st.success(f"P/B = {pb:.2f}｜合理範圍")
            else:
                st.warning(f"P/B = {pb:.2f}｜偏高，適合搭配 ROE 評估")
        if roe:
            st.markdown("**ROE 股東權益報酬率**")
            roe_pct = roe * 100
            if roe_pct >= 20:
                st.success(f"ROE = {roe_pct:.1f}%｜優秀（巴菲特標準 ≥ 15%）")
            elif roe_pct >= 12:
                st.success(f"ROE = {roe_pct:.1f}%｜良好")
            elif roe_pct >= 6:
                st.warning(f"ROE = {roe_pct:.1f}%｜普通")
            else:
                st.error(f"ROE = {roe_pct:.1f}%｜偏低")

# ── 損益趨勢 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("損益表趨勢（億元）")
trend = get_income_trend(income)
if trend.empty:
    st.info("無法取得損益表資料。")
else:
    items = {col: trend[col].tolist() for col in trend.columns if col in trend.columns}
    x = trend.index.tolist()
    st.plotly_chart(line_multi(x, items, "營收 / 毛利 / 營業利益 / 淨利（億元）"), use_container_width=True)
    with st.expander("原始數據"):
        st.dataframe(trend.T, use_container_width=True)

# ── 現金流品質 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("現金流品質分析")
cq = cashflow_quality(income, cashflow)
if cq["status"] == "no_data":
    st.info("無法取得現金流資料。")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("最新年度淨利", f"{cq['ni']:.1f} 億" if cq['ni'] else "—")
    c2.metric("最新年度營業現金流", f"{cq['ocf']:.1f} 億" if cq['ocf'] else "—")
    c3.metric("OCF / 淨利 比率", f"{cq['ratio']:.2f}" if cq['ratio'] else "—")

    if cq["status"] == "good":
        st.success("現金流品質優良：獲利有真實現金支撐，企業盈利含金量高。")
    elif cq["status"] == "ok":
        st.warning("現金流品質尚可：略有應計項目，持續觀察。")
    elif cq["status"] == "warn":
        st.error("現金流品質偏低：帳面獲利高但現金流入少，需關注應收帳款或庫存狀況。")

# ── 財報警示 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("財報健康訊號")
signals = check_signals(info, fins)
if not signals:
    st.info("資料不足，無法產生警示訊號。")
else:
    for s in signals:
        if s["risk"] in ("低",):
            st.success(f"**{s['icon']} {s['label']}**（風險：{s['risk']}）\n\n{s['detail']}")
        elif s["risk"] in ("中",):
            st.warning(f"**{s['icon']} {s['label']}**（風險：{s['risk']}）\n\n{s['detail']}")
        else:
            st.error(f"**{s['icon']} {s['label']}**（風險：{s['risk']}）\n\n{s['detail']}")

st.markdown("---")
st.caption("資料來源：Yahoo Finance。財報資料可能有 1–3 季延遲，僅供參考，非投資建議。")
