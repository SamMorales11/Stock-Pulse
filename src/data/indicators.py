# src/data/indicators.py
import pandas as pd
import pandas_ta as ta

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menambahkan indikator teknikal utama ke DataFrame menggunakan pandas-ta:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Moving Averages (SMA 20, SMA 50, EMA 200)
    - Bollinger Bands (Upper, Middle, Lower)
    - Stochastic Oscillator (%K, %D)
    """
    if df.empty or len(df) < 50:
        return df
    
    df = df.copy()
    
    # 1. RSI (14)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # 2. MACD (12, 26, 9)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        df['MACD'] = macd.iloc[:, 0]        # Garis MACD
        df['MACD_Hist'] = macd.iloc[:, 1]   # Histogram
        df['MACD_Signal'] = macd.iloc[:, 2] # Garis Signal
    
    # 3. Moving Averages
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    
    # 4. Bollinger Bands (20, 2) - Menggunakan indeks posisi .iloc agar aman dari KeyError
    bbands = ta.bbands(df['Close'], length=20, std=2)
    if bbands is not None and not bbands.empty:
        df['BB_Lower'] = bbands.iloc[:, 0]   # Lower Band
        df['BB_Middle'] = bbands.iloc[:, 1]  # Middle Band
        df['BB_Upper'] = bbands.iloc[:, 2]   # Upper Band
        
    # 5. Stochastic Oscillator (14, 3, 3)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
    if stoch is not None and not stoch.empty:
        df['STOCH_K'] = stoch.iloc[:, 0]    # %K
        df['STOCH_D'] = stoch.iloc[:, 1]    # %D
        
    # 6. Fitur tambahan: Daily Return & Rasio Volume
    df['Daily_Return'] = df['Close'].pct_change()
    df['Vol_SMA_20'] = ta.sma(df['Volume'], length=20)
    df['Vol_Ratio'] = df['Volume'] / (df['Vol_SMA_20'] + 1e-6)
    
    return df

def add_target_label(df: pd.DataFrame, future_days: int = 5, buy_threshold: float = 0.02) -> pd.DataFrame:
    """
    Membuat label target klasifikasi untuk pelatihan Machine Learning:
      1  (BUY)  : Jika harga naik >= 2% dalam 5 hari ke depan
      0  (WAIT) : Jika perubahan harga berada di antara -2% hingga +2%
     -1  (SELL) : Jika harga turun <= -2% dalam 5 hari ke depan
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Hitung return harga di N hari ke depan
    df['Future_Close'] = df['Close'].shift(-future_days)
    df['Future_Return'] = (df['Future_Close'] - df['Close']) / df['Close']
    
    def assign_label(ret):
        if pd.isna(ret):
            return None
        if ret >= buy_threshold:
            return 1   # BUY
        elif ret <= -buy_threshold:
            return -1  # SELL
        else:
            return 0   # WAIT
            
    df['Target'] = df['Future_Return'].apply(assign_label)
    return df