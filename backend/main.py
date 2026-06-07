import os
import requests
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

# ========================================================================
# ENDPOINT EXPERIMENT: LIVE PRICE TICKER (CRYPTO VIA BINANCE PUBLIC API)
# ========================================================================
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