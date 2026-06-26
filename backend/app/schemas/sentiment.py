from pydantic import BaseModel, Field


class NewsSentimentItem(BaseModel):
    title: str
    url: str
    time_published: str
    summary: str | None = None
    overall_sentiment_score: float = Field(
        ..., description="Skor sentimen dari -1 (sangat negatif) ke +1 (sangat positif)"
    )
    overall_sentiment_label: str = Field(
        ..., description="Label kategori, misal 'Bullish', 'Neutral', 'Bearish'"
    )


class NewsSentimentResponse(BaseModel):
    symbol: str
    articles: list[NewsSentimentItem]
    is_stale: bool = False
    source: str = "Alpha Vantage"