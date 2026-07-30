# src/models/predict.py
import joblib
import pandas as pd
from src.models.guardrails import apply_guardrails
from src.models.train import FEATURE_COLS

def predict_signal_for_stock(df_with_indicators: pd.DataFrame, model_path: str = "data/models/classifier_model.pkl") -> dict:
    """
    Mengambil baris data terbaru dan memprediksi sinyal harian (BUY NOW, WAIT, SELL).
    """
    if df_with_indicators.empty or len(df_with_indicators) < 50:
        return {"signal_code": 0, "signal_label": "WAIT", "reason": "Data kurang"}
    
    # Ambil baris data paling baru
    latest_row = df_with_indicators.iloc[-1]
    
    # Cek apakah fitur indikator lengkap
    features = latest_row[FEATURE_COLS].to_frame().T
    if features.isna().any().any():
        return {"signal_code": 0, "signal_label": "WAIT", "reason": "Indikator belum lengkap"}
    
    # Load Model
    try:
        model = joblib.load(model_path)
    except Exception as e:
        return {"signal_code": 0, "signal_label": "WAIT", "reason": f"Model error: {e}"}
    
    # Inferensi ML
    raw_signal = int(model.predict(features)[0])
    
    # Terapkan Guardrails
    final_signal, reason = apply_guardrails(raw_signal, latest_row)
    
    # Menerjemahkan Kode ke Label Teks
    label_map = {1: "BUY NOW", 0: "WAIT", -1: "SELL / AVOID"}
    
    return {
        "ticker": latest_row.get('Ticker', 'UNKNOWN'),
        "date": str(latest_row.get('Date', ''))[:10],
        "close": latest_row.get('Close'),
        "signal_code": final_signal,
        "signal_label": label_map.get(final_signal, "WAIT"),
        "reason": reason
    }