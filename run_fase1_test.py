# run_fase1_test.py
from config.settings import DEFAULT_TICKERS
from src.data.fetcher import fetch_multiple_stocks
from src.data.filters import filter_liquid_stocks

if __name__ == "__main__":
    print("=== TEST FASE 1: DATA INGESTION & LIQUIDITY FILTER ===")
    
    # 1. Fetch data (Ganti "6m" menjadi "6mo" atau "1y")
    raw_data = fetch_multiple_stocks(DEFAULT_TICKERS, period="6mo")
    
    # 2. Filter likuiditas
    liquid_stocks = filter_liquid_stocks(raw_data)
    
    # 3. Tampilkan sampel hasil
    print("\n=== HASIL DITERIMA ===")
    for ticker, df in liquid_stocks.items():
        last_price = df['Close'].iloc[-1]
        print(f"✓ {ticker} | Harga Terakhir: Rp {last_price:,.0f} | Total Data: {len(df)} baris")