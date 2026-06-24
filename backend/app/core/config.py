from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


def find_project_root(marker: str = "requirements.txt") -> Path:
    """Cari folder root dengan menelusuri ke atas sampai ketemu file marker."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / marker).exists():
            return current
        current = current.parent
    raise FileNotFoundError(f"Tidak ketemu root project (marker: {marker})")


ENV_PATH = find_project_root() / ".env"


class Settings(BaseSettings):
    alpha_vantage_api_key: str
    fred_api_key: str
    binance_api_key: str | None = None
    binance_api_secret: str | None = None

    # Tambahan sesuai .env kamu
    secret_key: str
    gemini_api_key: str
    finnhub_api_key: str
    database_url: str = "sqlite:///./justcallquant.db"

    app_name: str = "justcallquant API"
    app_version: str = "0.1.0"

    cache_ttl_macro: int = 60 * 60 * 24
    cache_ttl_fundamental: int = 60 * 60 * 6
    cache_ttl_technical: int = 60
    cache_ttl_sentiment: int = 60 * 30

    headers: str = "justcallquant-api/0.1.0 (contact: ardhiussalam06@gmail.com)"
    @property
    def default_header(self)->dict:
        """Header standar yang dipakai semua HTTP client ke API eksternal."""
        return {
            "Header": self.headers,
            "Accept": "application/json",
        }

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()