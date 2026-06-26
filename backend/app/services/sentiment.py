from core.cache import sentiment_cache, cache_key
from providers.alpha_vantage import get_news_sentiment_raw
from schemas.sentiment import NewsSentimentResponse, NewsSentimentItem
import logging

logger = logging.getLogger(__name__)


def fetch_news_sentiment(symbol: str, limit: int = 5) -> NewsSentimentResponse:
    key = cache_key("sentiment", symbol, limit)

    # 1. Cek cache dulu
    if key in sentiment_cache:
        cached_data = sentiment_cache[key]
        return NewsSentimentResponse(**cached_data, is_stale=False)

    # 2. Cache miss -> fetch dari Alpha Vantage
    try:
        raw = get_news_sentiment_raw(symbol, limit)

        # Khusus Alpha Vantage: cek apakah ini error message yang nyamar jadi 200 OK
        if "Information" in raw or "Error Message" in raw or "Note" in raw:
            error_msg = raw.get("Information") or raw.get("Error Message") or raw.get("Note")
            logger.warning(f"Alpha Vantage menolak request untuk {symbol}: {error_msg}")
            raise ValueError(f"Alpha Vantage error: {error_msg}")

        articles = [
            NewsSentimentItem(
                title=item["title"],
                url=item["url"],
                time_published=item["time_published"],
                summary=item.get("summary"),
                overall_sentiment_score=float(item["overall_sentiment_score"]),
                overall_sentiment_label=item["overall_sentiment_label"],
            )
            for item in raw.get("feed", [])
        ]

        result = {
            "symbol": symbol,
            "articles": articles,
            "source": "Alpha Vantage",
        }
        sentiment_cache[key] = result
        return NewsSentimentResponse(**result, is_stale=False)

    except Exception as e:
        logger.warning(f"Gagal fetch sentiment {symbol} dari Alpha Vantage: {e}")
        raise