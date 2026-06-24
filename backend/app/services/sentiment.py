import os
import requests
from fastapi import HTTPException


def fetch_news_sentiment(symbol: str, limit: int = 5):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    ticker = symbol.upper()
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=7)
        data = response.json()
        
        if "Note" in data or "Information" in data:
            return {
                "status": "limited",
                "message": "Kuota API Alpha Vantage habis (Limit tier gratis 25 request/hari) atau key belum diisi.",
                "sample_data": []
            }
            
        feed = data.get("feed", [])[:limit]
        formatted_news = []
        
        for item in feed:
            formatted_news.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "source": item.get("source"),
                "time_published": item.get("time_published"),
                "overall_sentiment_score": item.get("overall_sentiment_score"),
                "overall_sentiment_label": item.get("overall_sentiment_label")
            })
            
        return {
            "status": "success",
            "asset": ticker,
            "news_count": len(formatted_news),
            "news_feed": formatted_news
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))