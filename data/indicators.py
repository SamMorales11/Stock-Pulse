# src/data/indicators.py
import pandas as pd
import numpy as np

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menambahkan Indikator Teknikal Lengkap:
    - Moving Average (SMA_20, SMA_50)
    - RSI (14)
    - Bollinger Bands (BB_Upper, BB_Middle, BB_Lower)
    - MACD (MACD, MACD_Signal, MACD_Hist)
    """
    if df.empty:
        return df

    df = df.copy()

    # 1. Simple Moving Averages (SMA)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # 2. Relative Strength Index (RSI 14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 3. Bollinger Bands (20, 2)
    std_20 = df['Close'].rolling(window=20).std()
    df['BB_Middle'] = df['SMA_20']
    df['BB_Upper'] = df['BB_Middle'] + (std_20 * 2)
    df['BB_Lower'] = df['BB_Middle'] - (std_20 * 2)

    # 4. MACD (12, 26, 9)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df