# src/models/train.py
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, precision_score
from config.settings import DEFAULT_TICKERS
from src.data.fetcher import fetch_multiple_stocks
from src.data.indicators import add_technical_indicators, add_target_label

# Daftar fitur indikator teknikal yang akan dipelajari ML
FEATURE_COLS = [
    'RSI', 'MACD_Hist', 
    'Dist_SMA_20', 'Dist_SMA_50', 'Dist_EMA_200',
    'BB_Width', 'BB_Pos',
    'STOCH_K', 'STOCH_D', 'Daily_Return', 'Vol_Ratio'
]

def prepare_dataset(tickers: list) -> pd.DataFrame:
    """Mengumpulkan dan menggabungkan dataset dari berbagai saham."""
    print("Memproses dataset dari seluruh emiten...")
    all_data = []
    
    raw_dict = fetch_multiple_stocks(tickers, period="2y") # Pakai 2 tahun agar data latih melimpah
    
    for ticker, df in raw_dict.items():
        if df.empty or len(df) < 100:
            continue
        
        # Tambahkan indikator & label target
        df_ind = add_technical_indicators(df)
        df_labeled = add_target_label(df_ind, future_days=5, buy_threshold=0.02)
        
        # Hapus baris NaN
        df_clean = df_labeled.dropna(subset=FEATURE_COLS + ['Target'])
        all_data.append(df_clean)
        
    if not all_data:
        return pd.DataFrame()
        
    dataset = pd.concat(all_data, ignore_index=True)
    return dataset

def train_model():
    dataset = prepare_dataset(DEFAULT_TICKERS)
    
    if dataset.empty:
        print("[ERROR] Dataset kosong, pembentukan model dibatalkan.")
        return
    
    X = dataset[FEATURE_COLS]
    y = dataset['Target'].astype(int)
    
    print(f"Total baris data latih: {len(dataset)}")
    print(f"Distribusinya -> BUY (1): {(y==1).sum()}, WAIT (0): {(y==0).sum()}, SELL (-1): {(y==-1).sum()}")
    
    # Split Data: 80% Latih, 20% Uji
    split_idx = int(len(dataset) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Inisialisasi & Latih Model Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # Evaluasi
    y_pred = model.predict(X_test)
    print("\n=== LAPORAN EVALUASI MODEL ===")
    print(classification_report(y_test, y_pred))
    
    # Simpan Model ke Folder data/models/
    os.makedirs("data/models", exist_ok=True)
    model_path = "data/models/classifier_model.pkl"
    joblib.dump(model, model_path)
    print(f"Model berhasil disimpan ke: {model_path}")

if __name__ == "__main__":
    train_model()