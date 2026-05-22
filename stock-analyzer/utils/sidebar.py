import streamlit as st

_POPULAR = [
    ("台積電", "2330"), ("鴻海", "2317"),
    ("聯發科", "2454"), ("台達電", "2308"),
    ("富邦金", "2881"), ("中信金", "2891"),
    ("元大台50", "0050"), ("台灣大", "3045"),
]


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## 📈 台股分析平台")
        st.markdown("---")

        default = st.session_state.get("stock_code", "2330")
        code = st.text_input("股票代碼", value=default, placeholder="例：2330、0050")
        if code.strip() and code.strip() != st.session_state.get("stock_code"):
            st.session_state["stock_code"] = code.strip()

        st.caption("熱門快速切換")
        cols = st.columns(2)
        for i, (name, sym) in enumerate(_POPULAR):
            if cols[i % 2].button(name, key=f"_pop_{sym}", use_container_width=True):
                st.session_state["stock_code"] = sym
                st.rerun()

        st.markdown("---")
        st.info(f"目前查詢：**{st.session_state.get('stock_code', '2330')}**")
        st.caption("資料來源\nYahoo Finance · FinMind")

    return st.session_state.get("stock_code", "2330")
