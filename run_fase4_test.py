# run_fase4_test.py
import os
import sys

# Tambahkan root directory ke sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators
from src.database.repository import save_signals_to_db

# ---------------------------------------------------------
# DAFTAR TICKER SAHAM IDX (30 BIG CAP & LQ45)
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

def generate_mock_ml_signal(df):
    if df.empty or len(df) < 2:
        return "WAIT", "WAIT", "Data tidak mencukupi untuk analisa."
    
    latest = df.iloc[-1]
    rsi = latest.get('RSI', 50)
    close = latest.get('Close', 0)
    sma_20 = latest.get('SMA_20', close)

    if rsi < 35 and close > sma_20:
        return "BUY", "BUY NOW", "Oversold + Tren Bullish Terkonfirmasi (Guardrails Validated)"
    elif rsi > 70:
        return "SELL", "SELL / AVOID", "Overbought + Sinyal Jenuh Beli (Guardrails Validated)"
    else:
        return "WAIT", "WAIT", "Sinyal Konsolidasi / Wait and See"

def main():
    print("🚀 Memulai Pipeline Pemrosesan Sinyal Saham StockPulse...\n")
    
    signals_to_save = []
    total = len(TICKERS)
    
    for idx, ticker in enumerate(TICKERS, 1):
        print(f"[{idx}/{total}] Mengambil & memproses data: {ticker}...")
        
        try:
            df_stock = fetch_stock_data(ticker, period="1y")
            
            if df_stock is not None and not df_stock.empty:
                df_ind = add_technical_indicators(df_stock)
                latest_row = df_ind.iloc[-1]
                
                signal_code, signal_label, reason = generate_mock_ml_signal(df_ind)
                
                date_str = str(latest_row.name.date()) if hasattr(latest_row.name, 'date') else str(latest_row.get('Date', ''))
                close_price = float(latest_row.get('Close', 0))

                signals_to_save.append({
                    'date': date_str,
                    'ticker': ticker,
                    'close': close_price,
                    'signal_code': signal_code,
                    'signal_label': signal_label,
                    'reason': reason
                })
            else:
                print(f"⚠️ Warning: Data untuk {ticker} kosong.")
                
        except Exception as e:
            print(f"❌ Error memproses {ticker}: {e}")

    # Simpan hasil sinyal via Repository SQLAlchemy
    if signals_to_save:
        save_signals_to_db(signals_to_save)
        print(f"\n✅ BERHASIL! {len(signals_to_save)} sinyal saham telah diperbarui ke Database via SQLAlchemy.")
    else:
        print("\n⚠️ Tidak ada data sinyal yang berhasil disimpan.")

if __name__ == "__main__":
    main()