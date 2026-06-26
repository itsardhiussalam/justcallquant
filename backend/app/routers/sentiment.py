from fastapi import APIRouter
from services.sentiment import fetch_news_sentiment
from schemas.sentiment import NewsSentimentResponse

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment"])


@router.get("/news/{symbol}", response_model=NewsSentimentResponse)
def get_news_sentiment(symbol: str, limit: int = 5):
    """Mengambil sentimen berita pasar dari Alpha Vantage Service."""
    return fetch_news_sentiment(symbol, limit)