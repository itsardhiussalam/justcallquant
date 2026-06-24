from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class TechnicalIndicators(BaseModel):
    rsi: float | None = Field(default=None, description="Relative Strength Index, periode 14")
    sma_20: float | None = Field(default=None, description="Simple Moving Average 20 periode")
    ema_50: float | None = None


class CryptoHistoricalResponse(BaseModel):
    symbol: str
    interval: str
    candles: list[Candle]
    indicators: TechnicalIndicators
    is_stale: bool = False