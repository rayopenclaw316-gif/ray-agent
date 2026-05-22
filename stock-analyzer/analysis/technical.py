import pandas as pd
import numpy as np


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Close" not in df.columns:
        return df
    df = df.copy()
    c = df["Close"]

    # Moving averages
    for p in [5, 20, 60, 120, 240]:
        df[f"MA{p}"] = c.rolling(p).mean()

    # RSI(14)
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - 100 / (1 + rs)

    # MACD(12,26,9)
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

    # Bollinger Bands(20, 2σ)
    ma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    df["BB_upper"] = ma20 + 2 * std20
    df["BB_mid"] = ma20
    df["BB_lower"] = ma20 - 2 * std20

    # KD / Stochastic(9, 3, 3)
    lo9 = df["Low"].rolling(9).min()
    hi9 = df["High"].rolling(9).max()
    rng = (hi9 - lo9).replace(0, np.nan)
    rsv = (c - lo9) / rng * 100
    df["K"] = rsv.ewm(com=2, adjust=False).mean()
    df["D"] = df["K"].ewm(com=2, adjust=False).mean()

    return df
