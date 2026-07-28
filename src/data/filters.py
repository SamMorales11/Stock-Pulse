# src/data/filters.py
import pandas as pd
from typing import List, Dict
from config.settings import MIN_DAILY_TRANSACTION_VALUE, LIQUIDITY_CHECK_DAYS

def filter_liquid_stocks(
    data_dict: Dict[str, pd.DataFrame], 
    min_value: float = MIN_DAILY_TRANSACTION_VALUE, 
    days: int = LIQUIDITY_CHECK_DAYS
) -> Dict[str, pd.DataFrame]:
    """
    Menyaring saham berdasarkan rata-rata nilai transaksi harian (Close * Volume)
    selama N hari perdagangan terakhir.
    """
    liquid_data = {}
    
    for ticker, df in data_dict.items():
        if df.empty or len(df) < days:
            continue
        
        # Ambil N hari perdagangan terbaru
        recent_df = df.tail(days).copy()
        
        # Hitung estimasi nilai transaksi harian
        recent_df['TransactionValue'] = recent_df['Close'] * recent_df['Volume']
        avg_value = recent_df['TransactionValue'].mean()
        
        if avg_value >= min_value:
            liquid_data[ticker] = df
        else:
            print(f"[FILTERED] {ticker} dieliminasi (Rata-rata transaksi: Rp {avg_value:,.0f})")
            
    print(f"Saham lolos filter likuiditas: {len(liquid_data)} dari {len(data_dict)} emiten.")
    return liquid_data