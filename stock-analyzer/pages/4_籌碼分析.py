import streamlit as st
import pandas as pd
from utils.sidebar import render_sidebar
from data.finmind import get_institutional, get_margin_trading
from utils.charts import bar_signed, line_multi, C

st.set_page_config(page_title="籌碼分析", page_icon="🏦", layout="wide")
render_sidebar()
code = st.session_state.get("stock_code", "2330")

st.title(f"🏦 籌碼分析 — {code}")
st.caption("資料來源：FinMind（免費方案，每小時 30 次限制）")

# ── 三大法人 ──────────────────────────────────────────────────
st.subheader("三大法人買賣超（每日）")
with st.spinner("載入法人資料..."):
    df_inst = get_institutional(code)

if df_inst.empty:
    st.warning("無法取得法人資料。可能原因：FinMind 速率限制（請稍後再試）、或此代碼無資料。")
else:
    # FinMind 欄位：date, stock_id, name, buy, sell, net
    df_inst["date"] = pd.to_datetime(df_inst["date"])
    df_inst = df_inst.sort_values("date")

    investors = df_inst["name"].unique()
    tabs = st.tabs(list(investors) + ["合計"])

    for i, inv in enumerate(investors):
        sub = df_inst[df_inst["name"] == inv].copy()
        sub["net"] = pd.to_numeric(sub.get("net", sub.get("buy", 0)), errors="coerce").fillna(0)
        with tabs[i]:
            recent = sub.tail(60)
            col_l, col_r = st.columns([3, 1])
            with col_l:
                import plotly.graph_objects as go
                colors = [C["up"] if v >= 0 else C["down"] for v in recent["net"]]
                fig = go.Figure(go.Bar(x=recent["date"], y=recent["net"], marker_color=colors))
                fig.update_layout(title=f"{inv} 近 60 日買賣超（張）",
                                   template="plotly_dark", height=300, margin=dict(l=8,r=8,t=40,b=8))
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                total_net = recent["net"].sum()
                pos_days  = (recent["net"] > 0).sum()
                st.metric("近 60 日累計買超", f"{total_net:,.0f} 張",
                          delta_color="normal" if total_net >= 0 else "inverse")
                st.metric("買超天數", f"{pos_days} / {len(recent)} 天")

    # 合計
    with tabs[-1]:
        agg = df_inst.copy()
        agg["net"] = pd.to_numeric(agg.get("net", 0), errors="coerce").fillna(0)
        daily = agg.groupby("date")["net"].sum().reset_index().tail(60)
        colors = [C["up"] if v >= 0 else C["down"] for v in daily["net"]]
        fig = go.Figure(go.Bar(x=daily["date"], y=daily["net"], marker_color=colors))
        fig.update_layout(title="三大法人合計 近 60 日買賣超（張）",
                           template="plotly_dark", height=300, margin=dict(l=8,r=8,t=40,b=8))
        st.plotly_chart(fig, use_container_width=True)
        total = daily["net"].sum()
        st.metric("近 60 日合計", f"{total:,.0f} 張",
                  delta_color="normal" if total >= 0 else "inverse")

# ── 融資融券 ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("融資融券（近 60 日）")
with st.spinner("載入融資融券資料..."):
    df_mg = get_margin_trading(code)

if df_mg.empty:
    st.warning("無法取得融資融券資料（FinMind 速率限制或無資料）。")
else:
    df_mg["date"] = pd.to_datetime(df_mg["date"])
    df_mg = df_mg.sort_values("date").tail(60)

    # FinMind 欄位：MarginPurchaseBuy, MarginPurchaseSell, ShortSaleBuy, ShortSaleSell
    buy_col   = "MarginPurchaseBuy"   if "MarginPurchaseBuy"   in df_mg.columns else None
    short_col = "ShortSaleShortSell"  if "ShortSaleShortSell"  in df_mg.columns else None
    margin_bal = "MarginPurchaseBalance" if "MarginPurchaseBalance" in df_mg.columns else None
    short_bal  = "ShortSaleBalance"      if "ShortSaleBalance"      in df_mg.columns else None

    tab_a, tab_b = st.tabs(["融資餘額", "融券餘額"])
    with tab_a:
        if margin_bal and margin_bal in df_mg.columns:
            df_mg[margin_bal] = pd.to_numeric(df_mg[margin_bal], errors="coerce")
            import plotly.graph_objects as go
            fig = go.Figure(go.Scatter(x=df_mg["date"], y=df_mg[margin_bal],
                                       fill="tozeroy", line=dict(color=C["teal"], width=1.5)))
            fig.update_layout(title="融資餘額（張）", template="plotly_dark",
                               height=280, margin=dict(l=8,r=8,t=40,b=8))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("融資餘額上升 → 散戶加槓桿做多；快速上升後轉降常是短線頂部訊號。")
        else:
            st.info("此資料無融資餘額欄位。")

    with tab_b:
        if short_bal and short_bal in df_mg.columns:
            df_mg[short_bal] = pd.to_numeric(df_mg[short_bal], errors="coerce")
            fig = go.Figure(go.Scatter(x=df_mg["date"], y=df_mg[short_bal],
                                       fill="tozeroy", line=dict(color=C["down"], width=1.5)))
            fig.update_layout(title="融券餘額（張）", template="plotly_dark",
                               height=280, margin=dict(l=8,r=8,t=40,b=8))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("融券餘額高 → 空方力道強；若股價上漲而融券仍高，可能誘發軋空（Short Squeeze）。")
        else:
            st.info("此資料無融券餘額欄位。")
