from cachetools import TTLCache
from core.config import get_settings

settings = get_settings()

# Setiap jenis data punya cache instance sendiri dengan TTL berbeda
# maxsize dibatasi supaya memory tidak bocor tanpa kendali
macro_cache = TTLCache(maxsize=100, ttl=settings.cache_ttl_macro)
fundamental_cache = TTLCache(maxsize=200, ttl=settings.cache_ttl_fundamental)
technical_cache = TTLCache(maxsize=500, ttl=settings.cache_ttl_technical)
sentiment_cache = TTLCache(maxsize=200, ttl=settings.cache_ttl_sentiment)


def cache_key(*args) -> str:
    """Helper bikin key konsisten, misal cache_key('BTCUSDT', '1d', 30)"""
    return ":".join(str(a) for a in args)