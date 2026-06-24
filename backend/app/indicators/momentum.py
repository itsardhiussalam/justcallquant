import pandas as pd

def calculate_rsi(prices: list, period: int = 14) -> list:
    """
    Menghitung Relative Strength Index (RSI) menggunakan metode Wilder's EMA.
    """
    if len(prices) < period:
        return [None] * len(prices)
        
    series = pd.Series(prices)
    # Menghitung selisih harga dari bar sebelumnya
    delta = series.diff()
    
    # Memisahkan mana yang naik (gain) dan mana yang turun (loss)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Menghitung rata-rata bergerak eksponensial (EMA) sesuai standar industri keuangan
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    
    # Menghitung nilai RS dan konversi ke skala 0-100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return [None if pd.isna(x) else float(x) for x in rsi]