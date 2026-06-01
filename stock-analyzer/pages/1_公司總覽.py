import streamlit as st
from utils.sidebar import render_sidebar
from utils.autorefresh import maybe_autorefresh
from data.yf_data import get_stock_info, get_price_history, get_dividends
from analysis.technical import add_indicators
from utils.charts import candlestick, volume

st.set_page_config(page_title="公司總覽", page_icon="🏢", layout="wide")
render_sidebar()
maybe_autorefresh()
code = st.session_state.get("stock_code", "2330")

st.title(f"🏢 公司總覽 — {code}")

# ── 基本資訊 ──────────────────────────────────────────────────
with st.spinner("載入公司資訊..."):
    info = get_stock_info(code)

if not info:
    # May be a stale cache from a transient API failure — offer a one-click retry
    st.error(f"找不到 {code} 的股票資料。可能是快取了暫時性錯誤，或代碼不正確。")
    if st.button("🔄 清除快取並重試"):
        st.cache_data.clear()
        st.rerun()
    st.info("提示：台股代碼請輸入純數字（例如 2330、2485），OTC 股票也支援。")
    st.stop()

name = info.get("longName") or info.get("shortName") or code
st.subheader(name)

# Header metrics row
c1, c2, c3, c4, c5 = st.columns(5)
cur_price = info.get("currentPrice") or info.get("regularMarketPrice")
c1.metric("股價（元）", f"{cur_price:.2f}" if cur_price else "—")
mc = info.get("marketCap")
c2.metric("市值（億）", f"{mc/1e8:,.0f}" if mc else "—")
pe = info.get("trailingPE")
c3.metric("P/E 本益比", f"{pe:.1f} 倍" if pe else "—")
dy = info.get("dividendYield")
c4.metric("現金殖利率", f"{dy*100:.2f}%" if dy else "—")
hi52 = info.get("fiftyTwoWeekHigh")
lo52 = info.get("fiftyTwoWeekLow")
c5.metric("52週高 / 低", f"{hi52} / {lo52}" if hi52 else "—")

st.markdown("---")

# ── 股價走勢圖 ──────────────────────────────────────────────────
pcol, rcol = st.columns([4, 1])
with rcol:
    period = st.radio("時間範圍", ["3mo", "6mo", "1y", "2y", "5y"], index=2,
                       format_func=lambda x: {"3mo":"3個月","6mo":"6個月","1y":"1年","2y":"2年","5y":"5年"}[x])
    mas_sel = st.multiselect("顯示均線", ["MA5","MA20","MA60","MA120","MA240"],
                              default=["MA5","MA20","MA60"])

with pcol:
    with st.spinner("載入股價資料..."):
        df = get_price_history(code, period)
        df = add_indicators(df)

    if df.empty:
        st.error("無法取得股價資料。")
    else:
        ma_pairs = [(m, m) for m in mas_sel]
        st.plotly_chart(candlestick(df, f"{code} {name}", ma_pairs), use_container_width=True)
        st.plotly_chart(volume(df), use_container_width=True)

# ── 公司簡介 ──────────────────────────────────────────────────
bio = info.get("longBusinessSummary")
if bio:
    with st.expander("📄 公司業務簡介"):
        st.write(bio)

# ── 配息歷史 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("💰 配息歷史（近 10 次）")
with st.spinner("載入配息資料..."):
    divs = get_dividends(code)

if divs.empty:
    st.info("無配息記錄或 Yahoo Finance 暫無此資料。")
else:
    df_div = divs.tail(10).reset_index()
    df_div.columns = ["日期", "每股配息（元）"]
    df_div["日期"] = df_div["日期"].astype(str).str[:10]
    st.dataframe(df_div.sort_values("日期", ascending=False), use_container_width=True)
