import plotly.graph_objects as go
import pandas as pd
import numpy as np

C = {
    "up":     "#26A65B",
    "down":   "#E74C3C",
    "teal":   "#00D4AA",
    "blue":   "#3498DB",
    "orange": "#F39C12",
    "purple": "#9B59B6",
    "gray":   "#95A5A6",
    "pink":   "#E91E8C",
}
MA_COLORS = [C["teal"], C["orange"], C["purple"], C["blue"], C["gray"]]


def _base(fig: go.Figure, title: str = "", height: int = 450) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=height,
        margin=dict(l=8, r=8, t=40, b=8),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    return fig


def candlestick(df: pd.DataFrame, title: str = "", mas=None) -> go.Figure:
    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color=C["up"], decreasing_line_color=C["down"],
        name="K線",
    ))
    for i, (col, label) in enumerate(mas or []):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col], name=label,
                line=dict(color=MA_COLORS[i % 5], width=1.2), opacity=0.9,
            ))
    return _base(fig, title, 460)


def volume(df: pd.DataFrame) -> go.Figure:
    colors = [C["up"] if c >= o else C["down"] for c, o in zip(df["Close"], df["Open"])]
    fig = go.Figure(go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="成交量"))
    return _base(fig, "成交量", 160)


def rsi(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(y0=70, y1=100, fillcolor="red",   opacity=0.05, line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="green", opacity=0.05, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color="red",   opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI(14)",
                             line=dict(color=C["orange"], width=1.5)))
    fig.update_yaxes(range=[0, 100])
    return _base(fig, "RSI（14）", 200)


def macd(df: pd.DataFrame) -> go.Figure:
    hist_c = [C["up"] if v >= 0 else C["down"] for v in df["MACD_hist"].fillna(0)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], marker_color=hist_c, name="MACD柱"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],        name="MACD",   line=dict(color=C["blue"],   width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal", line=dict(color=C["orange"], width=1.5)))
    return _base(fig, "MACD（12, 26, 9）", 220)


def kd(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(y0=80, y1=100, fillcolor="red",   opacity=0.05, line_width=0)
    fig.add_hrect(y0=0,  y1=20,  fillcolor="green", opacity=0.05, line_width=0)
    fig.add_hline(y=80, line_dash="dash", line_color="red",   opacity=0.5)
    fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5)
    fig.add_trace(go.Scatter(x=df.index, y=df["K"], name="K值", line=dict(color=C["teal"],   width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["D"], name="D值", line=dict(color=C["orange"], width=1.5)))
    fig.update_yaxes(range=[0, 100])
    return _base(fig, "KD 指標（9日）", 200)


def line_multi(x, series: dict, title: str = "", height: int = 320) -> go.Figure:
    clrs = [C["teal"], C["blue"], C["orange"], C["purple"]]
    fig = go.Figure()
    for i, (name, y) in enumerate(series.items()):
        fig.add_trace(go.Scatter(
            x=x, y=y, name=name,
            line=dict(color=clrs[i % 4], width=2),
            mode="lines+markers", marker=dict(size=4),
        ))
    return _base(fig, title, height)


def bar_signed(x, y, title: str = "") -> go.Figure:
    colors = [C["up"] if v >= 0 else C["down"] for v in y]
    fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors))
    return _base(fig, title, 280)
