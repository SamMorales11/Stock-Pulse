# src/scheduler/cron_job.py
import time
from apscheduler.schedulers.background import BackgroundScheduler
from config.settings import DEFAULT_TICKERS
from src.data.fetcher import fetch_multiple_stocks
from src.data.filters import filter_liquid_stocks
from src.data.indicators import add_technical_indicators
from src.models.predict import predict_signal_for_stock
from src.database.repository import save_signal_to_db

def run_daily_pipeline():
    """Tugas otomatisasi harian: Fetch -> Filter -> Predict -> Save DB."""
    print("\n==================================================")
    print("🚀 MENJALANKAN PIPELINE HARIAN STOCKPULSE...")
    print("==================================================")

    # 1. Fetch & Filter Data
    raw_data = fetch_multiple_stocks(DEFAULT_TICKERS, period="1y")
    liquid_data = filter_liquid_stocks(raw_data)

    # 2. Proses Indikator & Prediksi
    for ticker, df in liquid_data.items():
        df_ind = add_technical_indicators(df)
        pred = predict_signal_for_stock(df_ind)

        # 3. Simpan ke SQLite Database
        save_signal_to_db(pred)
        print(f"✓ {ticker} -> {pred['signal_label']} (Tersimpan di DB)")

    print("==================================================")
    print("✅ PIPELINE HARIAN SELESAI & TER-UPDATE!")
    print("==================================================\n")

def start_scheduler():
    """Menjalankan Background Scheduler setiap jam 16:15 WIB (Senin-Jumat)."""
    scheduler = BackgroundScheduler()
    
    # Trigger setiap hari kerja pukul 16:15 WIB
    scheduler.add_job(
        run_daily_pipeline,
        'cron',
        day_of_week='mon-fri',
        hour=16,
        minute=15
    )
    
    scheduler.start()
    print("Scheduler aktif! Menunggu jadwal eksekusi jam 16:15 WIB...")
    
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()