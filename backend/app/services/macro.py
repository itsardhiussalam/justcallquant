from core.cache import macro_cache, cache_key
from providers.fred import get_series_observations
from schemas.macro import MacroIndicatorResponse, MacroObservation
import logging

logger = logging.getLogger(__name__)


def fetch_macro_indicator(indicator_name: str, limit: int = 6) -> MacroIndicatorResponse:
    key = cache_key("macro", indicator_name, limit)

    # 1. Cek cache dulu
    if key in macro_cache:
        cached_data = macro_cache[key]
        return MacroIndicatorResponse(**cached_data, is_stale=False)

    # 2. Cache miss -> coba fetch dari FRED
    try:
        raw = get_series_observations(indicator_name, limit)
        observations = [
            MacroObservation(date=obs["date"], value=_parse_value(obs["value"]))
            for obs in raw.get("observations", [])
        ]
        result = {
            "indicator_name": indicator_name,
            "observations": observations,
            "source": "FRED",
        }
        macro_cache[key] = result  # simpan versi mentah (dict) ke cache
        return MacroIndicatorResponse(**result, is_stale=False)

    except Exception as e:
        logger.warning(f"Gagal fetch {indicator_name} dari FRED: {e}")
        # 3. Fallback: kalau ada data lama di cache (meski TTL belum expire saat itu
        # tapi misal kita simpan juga last-known-good di tempat lain), kembalikan itu.
        # Untuk simplifikasi di sini, kita raise — tapi idealnya simpan last_known_good
        # di cache terpisah tanpa TTL sebagai fallback layer.
        raise


def _parse_value(raw_value: str) -> float | None:
    """FRED kadang return '.' untuk data kosong, bukan null."""
    if raw_value in (".", "", None):
        return None
    return float(raw_value)