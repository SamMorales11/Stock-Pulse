# src/models/guardrails.py
import pandas as pd

def apply_guardrails(raw_signal: int, latest_row: pd.Series) -> tuple[int, str]:
    """
    Memvalidasi sinyal ML dengan aturan teknikal fundamental:
    - Jika Sinyal ML = 1 (BUY), tapi harga < EMA_200 (Downtrend) -> Override ke 0 (WAIT)
    - Jika RSI > 70 (Overbought/Kejenuhan Beli) -> Override BUY ke 0 (WAIT)
    
    Mengembalikan: (Sinyal_Akhir, Alasan_Override)
    """
    close_price = latest_row.get('Close', 0)
    ema_200 = latest_row.get('EMA_200', 0)
    rsi = latest_row.get('RSI', 50)
    
    # Guardrail 1: Filter Downtrend Tren Panjang
    if raw_signal == 1 and pd.notna(ema_200) and close_price < ema_200:
        return 0, "Overridden to WAIT: Harga di bawah EMA 200 (Major Downtrend)"
        
    # Guardrail 2: Filter Jenuh Beli (Overbought)
    if raw_signal == 1 and pd.notna(rsi) and rsi > 70:
        return 0, "Overridden to WAIT: RSI > 70 (Overbought Risk)"
        
    return raw_signal, "Signal Validated by Guardrails"