import pandas as pd

def calculate_sma(prices: list, window: int = 20) -> list:
    """
    Menghitung Simple Moving Average (SMA) secara manual dengan Pandas.
    """
    if len(prices) < window:
        return [None] * len(prices)
        
    series = pd.Series(prices)
    # rolling(window) akan bergeser satu per satu bar untuk menghitung rata-rata
    sma = series.rolling(window=window).mean()
    
    # Mengubah NaN (Not a Number) milik Pandas menjadi None agar aman di JSON FastAPI
    return [None if pd.isna(x) else float(x) for x in sma]