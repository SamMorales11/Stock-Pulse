# src/data/fetcher.py
import yfinance as yf
import pandas as pd
from typing import List, Dict

def fetch_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Mengambil data OHLCV historis untuk satu ticker saham dari yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            print(f"[WARN] Data kosong untuk ticker: {ticker}")
            return pd.DataFrame()
        
        # Bersihkan index datetime agar menjadi kolom biasa
        df.reset_index(inplace=True)
        df['Ticker'] = ticker
        
        # Pastikan nama kolom standar
        cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]
        
        return df
    except Exception as e:
        print(f"[ERROR] Gagal menarik data {ticker}: {e}")
        return pd.DataFrame()

def fetch_multiple_stocks(tickers: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
    """
    Mengambil data OHLCV untuk daftar banyak ticker sekaligus.
    Mengembalikan dictionary {ticker: DataFrame}.
    """
    data_dict = {}
    print(f"Mengambil data untuk {len(tickers)} saham...")
    
    for ticker in tickers:
        df = fetch_stock_data(ticker, period=period)
        if not df.empty:
            data_dict[ticker] = df
            
    print(f"Berhasil menarik {len(data_dict)} data saham.")
    return data_dict