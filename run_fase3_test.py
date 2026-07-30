# run_fase3_test.py
from src.models.train import train_model
from src.models.predict import predict_signal_for_stock
from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators

if __name__ == "__main__":
    print("=== STEP 1: PELATIHAN MODEL MACHINE LEARNING ===")
    train_model()
    
    print("\n=== STEP 2: PENGUJIAN INFERENSI SINYAL HARIAN ===")
    test_tickers = ["BBCA.JK", "TLKM.JK", "GOTO.JK"]
    
    for ticker in test_tickers:
        df = fetch_stock_data(ticker, period="1y")
        df_ind = add_technical_indicators(df)
        
        result = predict_signal_for_stock(df_ind)
        print(f"\n[HASIL PREDIKSI] {result['ticker']}")
        print(f" Tanggal   : {result['date']}")
        print(f" Harga     : Rp {result['close']:,.0f}")
        print(f" Keputusan : >>> {result['signal_label']} <<<")
        print(f" Catatan   : {result['reason']}")