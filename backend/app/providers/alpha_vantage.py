import httpx
from core.config import get_settings

settings = get_settings()
BASE_URL = "https://www.alphavantage.co/query"


def get_news_sentiment_raw(symbol: str, limit: int = 5) -> dict:
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "limit": limit,
        "apikey": settings.alpha_vantage_api_key,
    }
    response = httpx.get(BASE_URL, params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()