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

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "FastAPI engine is running smoothly!",
        "database": "Connected to SQLite"
    }

# ENDPOINT EXPERIMENT: LIVE PRICE TICKER (CRYPTO VIA BINANCE PUBLIC API)
@app.get("/api/ticker/crypto/{symbol}")
def get_crypto_price(symbol: str):
    """
    Mengambil harga live cryptocurrency langsung dari API Publik Binance.
    Contoh input: BTCUSDT, ETHUSDT, atau SOLUSDT (Wajib UPPERCASE)
    """
    # Memastikan input simbol dalam huruf besar
    pair = symbol.upper()
    
    # URL API Publik Binance untuk harga ticker terakhir
    binance_url = f"https://data-api.binance.vision/api/v3/ticker/price?symbol={pair}"
    
    try:
        response = requests.get(binance_url, timeout=5)
        
        # Jika simbol tidak ditemukan di Binance (Error 400)
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
        raise HTTPException(
            status_code=503, 
            detail=f"Gagal terhubung ke server Binance: {str(e)}"
        )
    


# ENDPOINT HISTORIS: CANDLESTICK / KLINES (OHLCV)
@app.get("/api/ticker/crypto/historical/{symbol}")
def get_crypto_historical(symbol: str, interval: str = "1d", limit: int = 30):
    """
    Mengambil data historis candlestick (Klines) dari Binance.
    - interval: 1m, 1h, 1d, 1w (default: 1d / harian)
    - limit: jumlah candlestick yang ditarik (default: 30 hari terakhir)
    """
    pair = symbol.upper()
    
    # Menggunakan URL alternatif .vision yang aman dari blokir
    klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
    
    try:
        response = requests.get(klines_url, timeout=5)
        
        if response.status_code == 400:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbol '{pair}' atau interval tidak valid."
            )
            
        data = response.json()
        
        # Binance mengembalikan data dalam bentuk array mentah tanpa label.
        # Kita format ulang menjadi JSON (Dictionary) yang rapi dan siap pakai.
        formatted_data = []
        for candle in data:
            formatted_data.append({
                "open_time": candle[0],
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "close_time": candle[6]
            })
            
        return {
            "status": "success",
            "asset": pair,
            "interval": interval,
            "data_points": len(formatted_data),
            "historical_data": formatted_data
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Gagal menarik data historis: {str(e)}"
        )
    
# ENDPOINT HISTORIS: SAHAM & KOMODITAS (VIA YAHOO FINANCE)
@app.get("/api/ticker/market/{symbol}")
def get_market_data(symbol: str, period: str = "1mo"):
    """
    Mengambil data historis Saham, Indeks, atau Komoditas via Yahoo Finance.
    - IHSG (Indeks Indonesia): ^JKSE
    - Saham BCA: BBCA.JK
    - Saham Apple: AAPL
    - Emas (Gold Futures): GC=F
    - Minyak (Crude Oil Futures): CL=F
    - period: 1mo (1 bulan), 3mo (3 bulan), 1y (1 tahun)
    """
    ticker_symbol = symbol.upper()
    
    try:
        # Inisialisasi objek ticker yfinance
        ticker = yf.Ticker(ticker_symbol)
        
        # Ambil data historis berdasarkan periode (default 1 bulan, interval harian)
        hist = ticker.history(period=period)
        
        # Jika data kosong / simbol salah
        if hist.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbol pasar '{ticker_symbol}' tidak ditemukan atau tidak ada data."
            )
            
        # Format data Pandas DataFrame menjadi JSON Array yang rapi
        formatted_data = []
        for date, row in hist.iterrows():
            formatted_data.append({
                "date": date.strftime("%Y-%m-%d"), # Mengubah format tanggal menjadi teks rapi (YYYY-MM-DD)
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
            "data_points": len(formatted_data),
            "historical_data": formatted_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Terjadi kesalahan pada internal server: {str(e)}"
        )
    

