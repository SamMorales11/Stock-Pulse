# run_fase2_test.py
from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators, add_target_label

if __name__ == "__main__":
    print("=== TEST FASE 2: FEATURE ENGINEERING & INDICATORS ===")
    
    # 1. Fetch data 1 saham sampel (BBCA.JK, periode 1 tahun agar EMA_200 bisa dihitung)
    df = fetch_stock_data("BBCA.JK", period="1y")
    print(f"Data mentah ditarik: {len(df)} baris.")
    
    # 2. Tambahkan indikator teknikal
    df_with_indicators = add_technical_indicators(df)
    
    # 3. Tambahkan target label ML
    df_final = add_target_label(df_with_indicators, future_days=5, buy_threshold=0.02)
    
    # 4. Hapus baris NaN hasil kalkulasi periode awal indikator
    cleaned_df = df_final.dropna(subset=['RSI', 'MACD', 'SMA_20', 'STOCH_K'])
    
    print(f"Data bersih setelah ditambah indikator: {len(cleaned_df)} baris.\n")
    
    # Tampilkan 5 baris terakhir
    cols_to_show = ['Date', 'Close', 'RSI', 'MACD', 'SMA_20', 'STOCH_K', 'Target']
    print("=== SAMPEL 5 BARIS DATA TERAKHIR ===")
    print(cleaned_df[cols_to_show].tail())