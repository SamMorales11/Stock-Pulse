# run_fase4_test.py
from src.scheduler.cron_job import run_daily_pipeline
from src.database.repository import get_latest_signals

if __name__ == "__main__":
    print("=== TEST FASE 4: DATABASE & AUTOMATION PIPELINE ===")
    
    # Eksekusi pipeline
    run_daily_pipeline()
    
    # Cek isi database SQLite
    print("\n=== ISI DATABASE TERBARU (READ FROM SQLITE) ===")
    records = get_latest_signals()
    for r in records:
        print(f"[{r['date']}] {r['ticker']} | Rp {r['close']:,.0f} | Status: {r['signal_label']}")