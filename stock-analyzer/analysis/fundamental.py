import pandas as pd

# (yfinance key, 中文標籤, 單位, 格式字串)
RATIO_DEFS = [
    ("trailingPE",      "P/E 本益比",           "倍",  "{:.1f}"),
    ("priceToBook",     "P/B 股價淨值比",        "倍",  "{:.2f}"),
    ("dividendYield",   "現金殖利率",            "%",   "{:.2%}"),
    ("returnOnEquity",  "ROE 股東權益報酬率",     "%",   "{:.2%}"),
    ("returnOnAssets",  "ROA 資產報酬率",         "%",   "{:.2%}"),
    ("grossMargins",    "毛利率",                "%",   "{:.2%}"),
    ("operatingMargins","營業利益率",             "%",   "{:.2%}"),
    ("profitMargins",   "淨利率",                "%",   "{:.2%}"),
    ("debtToEquity",    "負債權益比 D/E",         "",    "{:.1f}"),
    ("currentRatio",    "流動比率",              "",    "{:.2f}"),
    ("quickRatio",      "速動比率",              "",    "{:.2f}"),
    ("revenueGrowth",   "營收成長率 (YoY)",       "%",   "{:.2%}"),
    ("earningsGrowth",  "獲利成長率 (YoY)",       "%",   "{:.2%}"),
]


def get_ratio_table(info: dict) -> pd.DataFrame:
    rows = []
    for key, label, unit, fmt in RATIO_DEFS:
        val = info.get(key)
        if val is None:
            continue
        try:
            display = fmt.format(val)
        except Exception:
            display = str(val)
        rows.append({"指標": label, "數值": display + (" " + unit if unit else "")})
    return pd.DataFrame(rows)


def get_income_trend(income: pd.DataFrame) -> pd.DataFrame:
    """回傳以億元為單位的損益趨勢（欄位=年份，列=項目）"""
    if income is None or income.empty:
        return pd.DataFrame()
    mapping = {
        "Total Revenue": "營收",
        "Gross Profit": "毛利",
        "Operating Income": "營業利益",
        "Net Income": "淨利",
    }
    rows = {}
    for key, label in mapping.items():
        if key in income.index:
            rows[label] = income.loc[key] / 1e8
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df.index = [str(c)[:10] for c in df.index]
    return df.sort_index()


def cashflow_quality(income: pd.DataFrame, cashflow: pd.DataFrame) -> dict:
    out = {"status": "no_data", "ni": None, "ocf": None, "ratio": None}
    if income is None or income.empty or cashflow is None or cashflow.empty:
        return out
    try:
        ni  = float(income.loc["Net Income"].iloc[0])   if "Net Income"         in income.index   else None
        ocf = float(cashflow.loc["Operating Cash Flow"].iloc[0]) if "Operating Cash Flow" in cashflow.index else None
        if ni is None or ocf is None:
            return out
        ratio = ocf / ni if ni != 0 else None
        out.update({"ni": ni / 1e8, "ocf": ocf / 1e8, "ratio": ratio,
                    "status": "good" if ratio and ratio >= 1.0
                               else "ok" if ratio and ratio >= 0.7
                               else "warn"})
    except Exception:
        pass
    return out
