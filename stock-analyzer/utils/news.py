import requests
import streamlit as st

_FC_KEY = "fc-0eeba87cf95b4d04a1be8014ccc0abe9"
_FC_URL = "https://api.firecrawl.dev/v1/search"


@st.cache_data(ttl=3600, show_spinner=False)
def search_news(query: str, limit: int = 5) -> list:
    """
    Firecrawl search for company news.
    Returns list of dicts with keys: title, url, description
    """
    try:
        r = requests.post(
            _FC_URL,
            headers={
                "Authorization": f"Bearer {_FC_KEY}",
                "Content-Type": "application/json",
            },
            json={"query": query, "limit": limit, "lang": "zh", "country": "tw"},
            timeout=30,
        )
        data = r.json()
        if data.get("success") and data.get("data"):
            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": (item.get("description") or "")[:300],
                }
                for item in data["data"]
                if item.get("title")
            ]
    except Exception:
        pass
    return []
