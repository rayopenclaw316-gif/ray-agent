import pandas as pd


def check_signals(info: dict, financials: dict) -> list:
    """回傳警示訊號列表，每項為 {icon, label, detail, risk}"""
    signals = []
    income   = financials.get("income",   pd.DataFrame())
    cashflow = financials.get("cashflow", pd.DataFrame())
    balance  = financials.get("balance",  pd.DataFrame())

    # 1. OCF vs 淨利
    if not income.empty and not cashflow.empty:
        try:
            ni_row  = income.loc["Net Income"]   if "Net Income"         in income.index   else None
            ocf_row = cashflow.loc["Operating Cash Flow"] if "Operating Cash Flow" in cashflow.index else None
            if ni_row is not None and ocf_row is not None:
                ni  = float(ni_row.iloc[0])
                ocf = float(ocf_row.iloc[0])
                if ni > 0:
                    ratio = ocf / ni
                    if ratio < 0.7:
                        signals.append({
                            "icon": "🔴", "risk": "高",
                            "label": "現金流品質警示",
                            "detail": f"OCF {ocf/1e8:.1f}億 vs 淨利 {ni/1e8:.1f}億，比率 {ratio:.2f} < 0.7。獲利可能包含大量應計項目（未收到現金）。",
                        })
                    else:
                        signals.append({
                            "icon": "🟢", "risk": "低",
                            "label": "現金流品質正常",
                            "detail": f"OCF {ocf/1e8:.1f}億 / 淨利 {ni/1e8:.1f}億 = {ratio:.2f}，現金支撐良好。",
                        })
        except Exception:
            pass

    # 2. 毛利率趨勢
    gm = info.get("grossMargins")
    if gm is not None and not income.empty and "Gross Profit" in income.index and "Total Revenue" in income.index:
        try:
            gp_series  = income.loc["Gross Profit"]
            rev_series = income.loc["Total Revenue"]
            if len(gp_series) >= 3:
                gm_hist = (gp_series / rev_series).dropna()
                if len(gm_hist) >= 3:
                    trend = gm_hist.iloc[0] - gm_hist.iloc[-1]
                    if trend < -0.05:
                        signals.append({
                            "icon": "🟡", "risk": "中",
                            "label": "毛利率持續下滑",
                            "detail": f"最近數年毛利率從 {gm_hist.iloc[-1]:.1%} 降至 {gm_hist.iloc[0]:.1%}，下滑 {abs(trend):.1%}。",
                        })
        except Exception:
            pass

    # 3. 負債急速上升
    if not balance.empty and "Total Debt" in balance.index:
        try:
            debt = balance.loc["Total Debt"].dropna()
            if len(debt) >= 2:
                chg = (debt.iloc[0] - debt.iloc[-1]) / abs(debt.iloc[-1]) if debt.iloc[-1] != 0 else 0
                if chg > 0.5:
                    signals.append({
                        "icon": "🟠", "risk": "中高",
                        "label": "總負債大幅增加",
                        "detail": f"近幾年總負債增加約 {chg:.1%}，需確認是否為業務擴張或財務壓力。",
                    })
        except Exception:
            pass

    # 4. 營收成長但淨利下滑
    rev_growth = info.get("revenueGrowth", 0) or 0
    earn_growth = info.get("earningsGrowth", 0) or 0
    if rev_growth > 0.05 and earn_growth < -0.1:
        signals.append({
            "icon": "🟡", "risk": "中",
            "label": "增收不增利",
            "detail": f"營收成長 {rev_growth:.1%} 但獲利下滑 {earn_growth:.1%}，需注意成本結構或業外損失。",
        })

    return signals
