import httpx
from core.config import get_settings

settings = get_settings()
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (justcallquant API client)"
}


def get_series_observations(series_id: str, limit: int = 6) -> dict:
    params = {
        "series_id": series_id,
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    response = httpx.get(BASE_URL, params=params, headers=settings.default_header, timeout=15.0)
    response.raise_for_status()
    return response.json()