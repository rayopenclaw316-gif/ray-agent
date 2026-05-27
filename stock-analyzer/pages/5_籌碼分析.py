import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.sidebar import render_sidebar
from utils.autorefresh import maybe_autorefresh
from data.twse_chip import get_institutional, get_margin_stock
from utils.charts import C, _base

st.set_page_config(page_title="籌碼分析", page_icon="🏦", layout="wide")
render_sidebar()
maybe_autorefresh()
code = st.session_state.get("stock_code", "2330")

st.title(f"🏦 籌碼分析 — {code}")
st.caption("資料來源：TWSE 官方 OpenAPI（免費、無 token 限制）")

# ── 三大法人 ──────────────────────────────────────────────────
st.subheader("三大法人買賣超（近 20 個交易日）")

with st.spinner("從 TWSE 逐日抓取法人資料（首次約需 10 秒，之後自動快取）..."):
    df_inst = get_institutional(code, days=20)

if df_inst.empty:
    st.warning("目前無法取得資料，可能是假日、休市日、或 TWSE 伺服器暫時無回應，請稍後重試。")
else:
    # 快速指標
    c1, c2, c3, c4 = st.columns(4)
    for col, key, label in [
        (c1, "外資",  "外資累計"),
        (c2, "投信",  "投信累計"),
        (c3, "自營商","自營商累計"),
        (c4, "合計",  "三大法人合計"),
    ]:
        total = int(df_inst[key].sum())
        col.metric(label, f"{total:,} 張",
                   delta_color="normal" if total >= 0 else "inverse")

    # 長條圖 tab
    tab_all, tab_f, tab_t, tab_d = st.tabs(["合計", "外資", "投信", "自營商"])

    def _bar(series: pd.Series, dates, title: str):
        colors = [C["up"] if v >= 0 else C["down"] for v in series]
        fig = go.Figure(go.Bar(x=dates, y=series, marker_color=colors))
        _base(fig, title, 280)
        return fig

    with tab_all:
        st.plotly_chart(_bar(df_inst["合計"], df_inst["日期"], "三大法人合計買賣超（張）"),
                        use_container_width=True)
    with tab_f:
        st.plotly_chart(_bar(df_inst["外資"], df_inst["日期"], "外資買賣超（張）"),
                        use_container_width=True)
    with tab_t:
        st.plotly_chart(_bar(df_inst["投信"], df_inst["日期"], "投信買賣超（張）"),
                        use_container_width=True)
    with tab_d:
        st.plotly_chart(_bar(df_inst["自營商"], df_inst["日期"], "自營商買賣超（張）"),
                        use_container_width=True)

    with st.expander("原始數據"):
        show = df_inst.copy()
        show["日期"] = show["日期"].astype(str).str[:10]
        st.dataframe(show.sort_values("日期", ascending=False), use_container_width=True)

# ── 融資融券 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("融資融券（今日快照）")

with st.spinner("載入融資融券資料..."):
    mg = get_margin_stock(code)

if not mg:
    st.warning("今日融資融券資料尚未更新（收盤後約 18:00 可取得），或此代碼無融資融券。")
else:
    def _i(val):
        s = str(val).replace(',', '').strip()
        return int(s) if s else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("融資今日餘額（張）", f"{_i(mg.get('融資今日餘額','0')):,}")
    c2.metric("融資買進（張）",      f"{_i(mg.get('融資買進','0')):,}")
    c3.metric("融券今日餘額（張）", f"{_i(mg.get('融券今日餘額','0')):,}")
    c4.metric("融券賣出（張）",      f"{_i(mg.get('融券賣出','0')):,}")

    # 券資比
    margin_bal = str(mg.get('融資今日餘額', '0')).replace(',', '').strip()
    short_bal  = str(mg.get('融券今日餘額', '0')).replace(',', '').strip()
    try:
        ratio = int(short_bal) / int(margin_bal) * 100 if int(margin_bal) > 0 else 0
        st.metric("券資比", f"{ratio:.1f}%",
                  help="融券餘額 ÷ 融資餘額。>30% 代表空方力道強，可能引發軋空。")
    except Exception:
        pass

    st.markdown("""
**判讀提示**
- 融資餘額持續上升 → 散戶加槓桿做多，注意高點出現後的「斷頭」壓力
- 融券餘額高 + 股價上漲 → 可能誘發**軋空（Short Squeeze）**
- 券資比 > 30% → 空方積極，多空拉鋸
""")
