# run_fase4_test.py
import os
import sys
import sqlite3

# Tambahkan root directory ke sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators

# Deteksi lokasi database SQLite
def get_db_path():
    path_models = os.path.join(os.path.dirname(__file__), 'data', 'models', 'database.sqlite')
    path_data = os.path.join(os.path.dirname(__file__), 'data', 'database.sqlite')
    
    if os.path.exists(path_models):
        return path_models
    elif os.path.exists(path_data):
        return path_data
    else:
        os.makedirs(os.path.dirname(path_models), exist_ok=True)
        return path_models

# ---------------------------------------------------------
# DAFTAR TICKER SAHAM IDX (BIG CAP & LQ45)
# ---------------------------------------------------------
TICKERS = [
    # Perbankan (Banking)
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
    
    # Konsumer & Retail (Consumer Goods)
    "UNVR.JK", "ICBP.JK", "INDF.JK", "AMRT.JK", "CPIN.JK", "KLBF.JK", "MYOR.JK",
    
    # Telekomunikasi & Teknologi
    "TLKM.JK", "ISAT.JK", "EXCL.JK", "GOTO.JK",
    
    # Energi & Pertambangan (Energy & Mining)
    "ADRO.JK", "PTBA.JK", "PGAS.JK", "ANTM.JK", "MDKA.JK", "ITMG.JK", "MEDC.JK", "HRUM.JK",
    
    # Otomotif, Infrastruktur & Industri
    "ASII.JK", "JSMR.JK", "UNTR.JK", "TPIA.JK", "BRPT.JK", "INTP.JK"
]

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ticker TEXT,
            close REAL,
            signal_label TEXT,
            reason TEXT
        )
    """)
    conn.commit()

def save_signals_to_db(conn, signals):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM signals") # Perbarui dengan sinyal terbaru
    
    for sig in signals:
        cursor.execute("""
            INSERT INTO signals (date, ticker, close, signal_label, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (sig['date'], sig['ticker'], sig['close'], sig['signal_label'], sig['reason']))
    conn.commit()

def generate_mock_ml_signal(df):
    if df.empty or len(df) < 2:
        return "WAIT", "Data tidak mencukupi untuk analisa."
    
    latest = df.iloc[-1]
    rsi = latest.get('RSI', 50)
    close = latest.get('Close', 0)
    sma_20 = latest.get('SMA_20', close)

    if rsi < 35 and close > sma_20:
        return "BUY NOW", "Oversold + Tren Bullish Terkonfirmasi (Guardrails Validated)"
    elif rsi > 70:
        return "SELL / AVOID", "Overbought + Sinyal Jenuh Beli (Guardrails Validated)"
    else:
        return "WAIT", "Sinyal Konsolidasi / Wait and See"

def main():
    print("🚀 Memulai Pipeline Pemrosesan Sinyal Saham StockPulse...\n")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    init_db(conn)
    
    signals_to_save = []
    total = len(TICKERS)
    
    for idx, ticker in enumerate(TICKERS, 1):
        print(f"[{idx}/{total}] Mengambil & memproses data: {ticker}...")
        
        try:
            df_stock = fetch_stock_data(ticker, period="1y")
            
            if df_stock is not None and not df_stock.empty:
                df_ind = add_technical_indicators(df_stock)
                latest_row = df_ind.iloc[-1]
                signal_label, reason = generate_mock_ml_signal(df_ind)
                
                date_str = str(latest_row.name.date()) if hasattr(latest_row.name, 'date') else str(latest_row.get('Date', ''))
                close_price = float(latest_row.get('Close', 0))

                signals_to_save.append({
                    'date': date_str,
                    'ticker': ticker,
                    'close': close_price,
                    'signal_label': signal_label,
                    'reason': reason
                })
            else:
                print(f"⚠️ Warning: Data untuk {ticker} kosong.")
                
        except Exception as e:
            print(f"❌ Error memproses {ticker}: {e}")

    if signals_to_save:
        save_signals_to_db(conn, signals_to_save)
        print(f"\n✅ BERHASIL! {len(signals_to_save)} sinyal saham telah diperbarui ke Database SQLite.")
    else:
        print("\n⚠️ Tidak ada data sinyal yang berhasil disimpan.")
        
    conn.close()

if __name__ == "__main__":
    main()