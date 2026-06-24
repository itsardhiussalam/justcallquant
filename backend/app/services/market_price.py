import os
import requests
import yfinance as yf 
from fastapi import HTTPException
from indicators import calculate_sma, calculate_rsi


def fetch_crypto_price(symbol: str):
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


def fetch_crypto_historical(symbol: str, interval: str = "1d", limit: int = 30):
    pair = symbol.upper()
    klines_url = f"https://data-api.binance.vision/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
    
    try:
        response = requests.get(klines_url, timeout=5)
        if response.status_code == 400:
            raise HTTPException(status_code=404, detail=f"Simbol '{pair}' atau interval tidak valid.")
            
        data = response.json()
        close_prices = [float(candle[4]) for candle in data]
        
        sma_20_values = calculate_sma(close_prices, window=20)
        rsi_14_values = calculate_rsi(close_prices, period=14)
        
        formatted_data = []
        for idx, candle in enumerate(data):
            formatted_data.append({
                "timestamp": int(candle[0] / 1000),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "technical": {
                    "sma_20": sma_20_values[idx],
                    "rsi_14": rsi_14_values[idx]
                }
            })
            
        return {
            "status": "success",
            "asset": pair,
            "interval": interval,
            "summary": {
                "latest_close": close_prices[-1],
                "latest_rsi_14": rsi_14_values[-1],
                "latest_sma_20": sma_20_values[-1]
            },
            "historical_data": formatted_data
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Gagal menarik data historis: {str(e)}")


def fetch_market_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    ticker_symbol = symbol.upper()
    
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
            
        close_prices = hist["Close"].tolist()
        sma_20_values = calculate_sma(close_prices, window=20)
        rsi_14_values = calculate_rsi(close_prices, period=14)
        
        formatted_data = []
        for idx, (date, row) in enumerate(hist.iterrows()):
            formatted_data.append({
                "date": date.strftime("%Y-%m-%d %H:%M:%S") if interval != "1d" else date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "technical": {
                    "sma_20": sma_20_values[idx],
                    "rsi_14": rsi_14_values[idx]
                }
            })
            
        return {
            "status": "success",
            "asset": ticker_symbol,
            "period": period,
            "interval": interval,
            "summary": {
                "latest_close": close_prices[-1],
                "latest_rsi_14": rsi_14_values[-1],
                "latest_sma_20": sma_20_values[-1]
            },
            "historical_data": formatted_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada internal server: {str(e)}")


