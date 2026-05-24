import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.sidebar import render_sidebar
from utils.autorefresh import maybe_autorefresh
from data.yf_data import get_stock_info, get_price_history

st.set_page_config(page_title="同業比較", page_icon="⚖️", layout="wide")
render_sidebar()
maybe_autorefresh()

code = st.session_state.get("stock_code", "2330")
st.title(f"⚖️ 同業比較 — {code}")

# ══════════════════════════════════════════════════════════════
# 同業群組定義
# ══════════════════════════════════════════════════════════════

PEER_GROUPS = {
    "2330": {"群組": "晶圓代工", "成員": [("台積電","2330"),("聯電","2303"),("世界先進","5347"),("力積電","6770")]},
    "2303": {"群組": "晶圓代工", "成員": [("聯電","2303"),("台積電","2330"),("世界先進","5347"),("力積電","6770")]},
    "5347": {"群組": "晶圓代工（成熟製程）", "成員": [("世界先進","5347"),("聯電","2303"),("力積電","6770")]},
    "6770": {"群組": "晶圓代工", "成員": [("力積電","6770"),("聯電","2303"),("世界先進","5347")]},
    "2454": {"群組": "IC 設計", "成員": [("聯發科","2454"),("聯詠","3034"),("瑞昱","2379"),("矽力-KY","6415")]},
    "3034": {"群組": "IC 設計（顯示驅動）", "成員": [("聯詠","3034"),("聯發科","2454"),("瑞昱","2379"),("奇景光電","3481")]},
    "2379": {"群組": "IC 設計（網通）", "成員": [("瑞昱","2379"),("聯發科","2454"),("聯詠","3034")]},
    "6415": {"群組": "IC 設計（電源）", "成員": [("矽力-KY","6415"),("聯發科","2454"),("瑞昱","2379")]},
    "2317": {"群組": "EMS 電子代工", "成員": [("鴻海","2317"),("廣達","2382"),("緯創","3231"),("仁寶","2324")]},
    "2382": {"群組": "伺服器 / 筆電 ODM", "成員": [("廣達","2382"),("緯創","3231"),("英業達","2356"),("仁寶","2324")]},
    "3231": {"群組": "EMS / ODM", "成員": [("緯創","3231"),("廣達","2382"),("英業達","2356"),("仁寶","2324")]},
    "2324": {"群組": "筆電 ODM", "成員": [("仁寶","2324"),("廣達","2382"),("緯創","3231"),("英業達","2356")]},
    "2356": {"群組": "伺服器 ODM", "成員": [("英業達","2356"),("廣達","2382"),("緯創","3231")]},
    "4938": {"群組": "EMS 代工", "成員": [("和碩","4938"),("鴻海","2317"),("廣達","2382")]},
    "2308": {"群組": "電源管理 / 工控", "成員": [("台達電","2308"),("光寶科","2301"),("研華","2395")]},
    "2301": {"群組": "電源管理 / 光電", "成員": [("光寶科","2301"),("台達電","2308"),("研華","2395")]},
    "2395": {"群組": "工業電腦 / 嵌入式", "成員": [("研華","2395"),("台達電","2308"),("凌華","6166")]},
    "2327": {"群組": "被動元件（MLCC）", "成員": [("國巨","2327"),("華新科","2492"),("禾伸堂","3026"),("信昌電","6173")]},
    "2492": {"群組": "被動元件（電容）", "成員": [("華新科","2492"),("國巨","2327"),("禾伸堂","3026")]},
    "3026": {"群組": "被動元件", "成員": [("禾伸堂","3026"),("國巨","2327"),("華新科","2492")]},
    "3711": {"群組": "IC 封裝測試（OSAT）", "成員": [("日月光","3711"),("力成","6239"),("南茂","8150"),("京元電","2449")]},
    "6239": {"群組": "IC 封裝測試", "成員": [("力成","6239"),("日月光","3711"),("南茂","8150"),("京元電","2449")]},
    "8150": {"群組": "IC 封裝測試", "成員": [("南茂","8150"),("日月光","3711"),("力成","6239"),("京元電","2449")]},
    "2449": {"群組": "IC 測試", "成員": [("京元電","2449"),("日月光","3711"),("力成","6239")]},
    "2603": {"群組": "貨櫃航運", "成員": [("長榮","2603"),("陽明","2609"),("萬海","2615")]},
    "2609": {"群組": "貨櫃航運", "成員": [("陽明","2609"),("長榮","2603"),("萬海","2615")]},
    "2615": {"群組": "貨櫃航運", "成員": [("萬海","2615"),("長榮","2603"),("陽明","2609")]},
    "2881": {"群組": "金融控股", "成員": [("富邦金","2881"),("中信金","2891"),("國泰金","2882"),("兆豐金","2886")]},
    "2891": {"群組": "金融控股", "成員": [("中信金","2891"),("富邦金","2881"),("國泰金","2882"),("玉山金","2884")]},
    "2882": {"群組": "金融控股", "成員": [("國泰金","2882"),("富邦金","2881"),("中信金","2891"),("兆豐金","2886")]},
    "2886": {"群組": "金融控股", "成員": [("兆豐金","2886"),("富邦金","2881"),("中信金","2891"),("第一金","2892")]},
    "2884": {"群組": "金融控股", "成員": [("玉山金","2884"),("中信金","2891"),("富邦金","2881"),("兆豐金","2886")]},
    "2892": {"群組": "金融控股", "成員": [("第一金","2892"),("兆豐金","2886"),("富邦金","2881"),("國泰金","2882")]},
    "0050": {"群組": "台股 ETF", "成員": [("元大台50","0050"),("富邦台50","006208"),("元大高股息","0056"),("國泰永續高股息","00878")]},
    "006208": {"群組": "台股 ETF", "成員": [("富邦台50","006208"),("元大台50","0050"),("元大高股息","0056")]},
    "0056": {"群組": "高股息 ETF", "成員": [("元大高股息","0056"),("國泰永續高股息","00878"),("元大台50","0050")]},
    "00878": {"群組": "ESG / 高股息 ETF", "成員": [("國泰永續高股息","00878"),("元大高股息","0056"),("元大台50","0050")]},
    "2412": {"群組": "電信服務", "成員": [("中華電","2412"),("台灣大","3045"),("遠傳","4904")]},
    "3045": {"群組": "電信服務", "成員": [("台灣大","3045"),("中華電","2412"),("遠傳","4904")]},
    "4904": {"群組": "電信服務", "成員": [("遠傳","4904"),("中華電","2412"),("台灣大","3045")]},
    "1301": {"群組": "石化原料（台塑四寶）", "成員": [("台塑","1301"),("南亞","1303"),("台化","1326"),("台塑化","6505")]},
    "1303": {"群組": "石化（台塑四寶）", "成員": [("南亞","1303"),("台塑","1301"),("台化","1326"),("台塑化","6505")]},
    "1326": {"群組": "石化（台塑四寶）", "成員": [("台化","1326"),("台塑","1301"),("南亞","1303"),("台塑化","6505")]},
    "6505": {"群組": "石化煉油（台塑四寶）", "成員": [("台塑化","6505"),("台塑","1301"),("南亞","1303"),("台化","1326")]},
}

# ══════════════════════════════════════════════════════════════
# 資料載入
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800, show_spinner=False)
def _info(sym):
    return get_stock_info(sym)


def build_comparison(members):
    display_rows = []
    raw_rows = []

    for name, sym in members:
        info = _info(sym)
        mc    = info.get("marketCap")
        pe    = info.get("trailingPE")
        pb    = info.get("priceToBook")
        roe   = info.get("returnOnEquity")
        gm    = info.get("grossMargins")
        dy    = info.get("dividendYield")
        eps   = info.get("trailingEps")
        price = info.get("currentPrice") or info.get("regularMarketPrice")

        display_rows.append({
            "公司":       name,
            "代號":       sym,
            "股價（元）": f"{price:.1f}"        if price else "—",
            "市值（億）": f"{mc/1e8:,.0f}"       if mc    else "—",
            "P/E":        f"{pe:.1f}"             if pe    else "—",
            "P/B":        f"{pb:.2f}"             if pb    else "—",
            "ROE（%）":   f"{roe*100:.1f}"        if roe   else "—",
            "毛利率（%）":f"{gm*100:.1f}"         if gm    else "—",
            "殖利率（%）":f"{dy*100:.2f}"         if dy    else "—",
            "EPS":        f"{eps:.2f}"            if eps   else "—",
        })
        raw_rows.append({
            "公司":       name,
            "P/E":        pe,
            "P/B":        pb,
            "ROE（%）":   roe * 100 if roe is not None else None,
            "毛利率（%）":gm  * 100 if gm  is not None else None,
            "殖利率（%）":dy  * 100 if dy  is not None else None,
        })

    return pd.DataFrame(display_rows), pd.DataFrame(raw_rows)


# ══════════════════════════════════════════════════════════════
# 同業選擇
# ══════════════════════════════════════════════════════════════

if code in PEER_GROUPS:
    group_info = PEER_GROUPS[code]
    members = group_info["成員"]
    st.caption(f"群組：**{group_info['群組']}**　｜　共 {len(members)} 家公司")
else:
    st.warning("此股票尚無預設同業群組，請手動輸入同業代碼。")
    custom = st.text_input(
        "輸入同業代碼（逗號分隔）",
        placeholder="例：2330,2303,5347",
        help="台股代碼直接輸入（不需加 .TW）",
    )
    if custom.strip():
        syms = [c.strip() for c in custom.split(",") if c.strip()]
        # ensure the main code is included
        if code not in syms:
            syms.insert(0, code)
        members = [(s, s) for s in syms]
    else:
        members = [(code, code)]
    st.caption(f"自訂比較清單：{', '.join(s for _, s in members)}")

# ══════════════════════════════════════════════════════════════
# 指標比較表
# ══════════════════════════════════════════════════════════════

st.subheader("📊 財務指標比較")
st.caption("資料來源：Yahoo Finance（15 分鐘延遲）")

with st.spinner("載入各公司財務資料..."):
    df_display, df_raw = build_comparison(members)

if not df_display.empty:
    # Highlight current stock row
    main_name = next((n for n, s in members if s == code), code)

    def highlight_main(row):
        return ["background-color: rgba(0,200,255,0.15)" if row["公司"] == main_name else ""
                for _ in row]

    styled = df_display.set_index("公司").style.apply(highlight_main, axis=1)
    st.dataframe(styled, use_container_width=True, height=min(len(members) * 38 + 60, 320))

# ══════════════════════════════════════════════════════════════
# 相對走勢圖
# ══════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("📈 股價相對走勢（標準化）")

period_map = {"3個月": "3mo", "6個月": "6mo", "1年": "1y", "2年": "2y"}
sel_period = st.radio("時間範圍", list(period_map.keys()), index=2, horizontal=True)
period = period_map[sel_period]

COLORS = ["#00C8FF", "#FF6B35", "#26A65B", "#FFD93D", "#C77DFF", "#FF6B6B", "#A8E6CF"]

with st.spinner("載入股價歷史..."):
    fig_price = go.Figure()
    for i, (name, sym) in enumerate(members):
        df_p = get_price_history(sym, period)
        if df_p.empty:
            continue
        close = df_p["Close"].dropna()
        if len(close) < 5:
            continue
        norm = close / close.iloc[0] * 100
        is_main = (sym == code)
        fig_price.add_trace(go.Scatter(
            x=norm.index,
            y=norm.values,
            name=name,
            line=dict(
                color=COLORS[i % len(COLORS)],
                width=3 if is_main else 1.5,
                dash="solid" if is_main else "dot",
            ),
            hovertemplate=f"{name}: %{{y:.1f}}<extra></extra>",
        ))

    fig_price.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                        annotation_text="起始基準")
    fig_price.update_layout(
        title=f"股價相對走勢（起始日 = 100）",
        template="plotly_dark",
        height=420,
        margin=dict(l=8, r=8, t=44, b=56),
        yaxis_title="相對指數",
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_price, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 各指標長條圖
# ══════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("📉 單一指標比較")

metric_cols = ["P/E", "P/B", "ROE（%）", "毛利率（%）", "殖利率（%）"]
sel_metric = st.selectbox("選擇指標", metric_cols)

if not df_raw.empty and sel_metric in df_raw.columns:
    chart_df = df_raw[["公司", sel_metric]].copy()
    chart_df[sel_metric] = pd.to_numeric(chart_df[sel_metric], errors="coerce")
    chart_df = chart_df.dropna(subset=[sel_metric])

    if not chart_df.empty:
        main_name = next((n for n, s in members if s == code), code)
        bar_colors = [
            "#FF6B35" if row["公司"] == main_name else "#00C8FF"
            for _, row in chart_df.iterrows()
        ]
        fig_bar = go.Figure(go.Bar(
            x=chart_df["公司"],
            y=chart_df[sel_metric],
            marker_color=bar_colors,
            text=[f"{v:.2f}" for v in chart_df[sel_metric]],
            textposition="outside",
        ))
        fig_bar.update_layout(
            title=f"{sel_metric} 比較（橘色 = {main_name}）",
            template="plotly_dark",
            height=340,
            margin=dict(l=8, r=8, t=44, b=8),
            yaxis_title=sel_metric,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info(f"目前無法取得 {sel_metric} 資料（可能是 ETF 或缺乏財報資料）。")
