import os
import requests
import yfinance as yf 
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Inisialisasi FastAPI app
app = FastAPI(
    title="justcallquant API",
    description="Backend Core Engine untuk Analisis Finansial & AI Agent",
    version="0.1.0"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "FastAPI engine is running smoothly!",
        "database": "Connected to SQLite"
    }

# ========================================================================
# 1. CRYPTO ENGINE (VIA BINANCE PUBLIC API - BEBAS BLOKIR)
# ========================================================================

@app.get("/api/ticker/crypto/{symbol}")
def get_crypto_price(symbol: str):
    """
    Mengambil harga live cryptocurrency langsung dari API Publik Binance.
    Contoh: BTCUSDT, ETHUSDT, SOLUSDT
    """
    pair = symbol.upper()
    binance_url = f"https://data-api.binance.vision/api/v3/ticker/price?symbol={pair}"
    
    try:
        response = requests.get(binance_url, timeout=5)
        if response.status_code == 400:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbol trading '{pair}' tidak ditemukan di pasar Binance."
            )
        data = response.json()
        return {
            "status": "success",
            "asset": data["symbol"],
            "live_price": float(data["price"]),
            "provider": "Binance Public API"
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Gagal terhubung ke server Binance: {str(e)}")

@app.get("/api/ticker/crypto/historical/{symbol}")
def get_crypto_historical(symbol: str, interval: str = "1d", limit: int = 30):
    """
    Mengambil data historis candlestick (Klines) Kripto dari Binance.
    - interval: 1m, 5m, 15m, 1h, 1d, 1w
    - limit: jumlah bar candlestick yang ditarik
    """
    pair = symbol.upper()
    klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
    
    try:
        response = requests.get(klines_url, timeout=5)
        if response.status_code == 400:
            raise HTTPException(status_code=404, detail=f"Simbol '{pair}' atau interval tidak valid.")
            
        data = response.json()
        formatted_data = []
        for candle in data:
            formatted_data.append({
                "timestamp": int(candle[0] / 1000), # Dikonversi ke detik (UNIX Timestamp)
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            })
            
        return {
            "status": "success",
            "asset": pair,
            "interval": interval,
            "data_points": len(formatted_data),
            "historical_data": formatted_data
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Gagal menarik data historis: {str(e)}")

# ========================================================================
# 2. TRADITIONAL MARKET ENGINE (VIA YAHOO FINANCE - SUPPORT INTRADAY)
# ========================================================================

@app.get("/api/ticker/market/{symbol}")
def get_market_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """
    Mengambil data historis Saham, Indeks, atau Komoditas via Yahoo Finance.
    """
    ticker_symbol = symbol.upper()
    
    # OTOMATISASI: Jika interval menitan dan period terlalu sempit (1d), 
    # kita naikkan ke 5d secara otomatis agar tidak terjadi hist.empty di hari Senin/bursa baru buka.
    if interval in ["1m", "5m", "15m"] and period == "1d":
        period = "5d"
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbol pasar '{ticker_symbol}' tidak ditemukan atau tidak ada data pada timeframe ini."
            )
            
        formatted_data = []
        for date, row in hist.iterrows():
            formatted_data.append({
                "date": date.strftime("%Y-%m-%d %H:%M:%S") if interval != "1d" else date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })
            
        return {
            "status": "success",
            "asset": ticker_symbol,
            "period": period,
            "interval": interval,
            "data_points": len(formatted_data),
            "historical_data": formatted_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada internal server: {str(e)}")

# ========================================================================
# 3. SENTIMENT ENGINE (VIA ALPHA VANTAGE)
# ========================================================================

@app.get("/api/sentiment/news/{symbol}")
def get_news_sentiment(symbol: str, limit: int = 5):
    """
    Menarik berita finansial global terbaru beserta skor sentimennya dari Alpha Vantage.
    """
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

# ========================================================================
# 4. MACROECONOMIC ENGINE (VIA FRED API)
# ========================================================================

FRED_SERIES_MAPPING = {
    "interest_rate": "FEDFUNDS",
    "inflation": "CPIAUCSL",
    "unemployment": "UNRATE",
    "gdp": "GDPC1"
}

@app.get("/api/macro/indicators/{indicator_name}")
def get_macro_indicator(indicator_name: str, limit: int = 6):
    """
    Mengambil data makroekonomi historis dari FRED API berdasarkan nama indikator.
    """
    api_key = os.getenv("FRED_API_KEY")
    
    if not api_key or "masukkan" in api_key:
        raise HTTPException(status_code=400, detail="FRED_API_KEY belum dikonfigurasi di file .env")
        
    name_clean = indicator_name.lower()
    if name_clean not in FRED_SERIES_MAPPING:
        raise HTTPException(
            status_code=400,
            detail=f"Indikator '{indicator_name}' tidak didukung. Pilih: interest_rate, inflation, unemployment, atau gdp."
        )
        
    series_id = FRED_SERIES_MAPPING[name_clean]
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"FRED API Error: Status {response.status_code}")
            
        raw_data = response.json()
        observations = raw_data.get("observations", [])
        
        formatted_trends = []
        for obs in observations:
            formatted_trends.append({
                "date": obs.get("date"),
                "value": float(obs.get("value")) if obs.get("value") != "." else None
            })
            
        formatted_trends.reverse()
        
        return {
            "status": "success",
            "indicator": name_clean,
            "fred_series_id": series_id,
            "unit": "Percentage (%)" if name_clean != "gdp" else "Billions of Chained 2017 Dollars",
            "current_value": formatted_trends[-1]["value"] if formatted_trends else None,
            "data_points": len(formatted_trends),
            "trends": formatted_trends
        }
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Koneksi ke server FRED API mengalami timeout.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses data makro: {str(e)}")