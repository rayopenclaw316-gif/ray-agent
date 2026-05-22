"""
台股交易時間（09:00–13:30）內每 10 分鐘自動重整一次頁面。
收盤後或非交易日則不觸發。
"""
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def _is_trading() -> bool:
    now = datetime.now(ZoneInfo("Asia/Taipei"))
    if now.weekday() >= 5:          # 週六、週日
        return False
    h, m = now.hour, now.minute
    return (h > 9 or (h == 9 and m >= 0)) and (h < 13 or (h == 13 and m < 30))


def maybe_autorefresh(interval_ms: int = 600_000):
    """在交易時間內加入自動更新 badge；收盤後靜默。"""
    try:
        from streamlit_autorefresh import st_autorefresh
        if _is_trading():
            st_autorefresh(interval=interval_ms, key="mkt_autorefresh")
            st.caption("🔄 交易時段中，每 10 分鐘自動更新一次")
    except ImportError:
        pass  # 套件未安裝時不報錯，功能靜默關閉
