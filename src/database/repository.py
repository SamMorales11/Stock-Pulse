# src/database/repository.py
from sqlalchemy.orm import Session
from src.database.db import SessionLocal, SignalHistory, init_db

def save_signal_to_db(signal_data: dict):
    """Menyimpan atau memperbarui hasil sinyal saham harian ke SQLite."""
    init_db()
    db: Session = SessionLocal()
    try:
        # Cek apakah sinyal untuk ticker dan tanggal ini sudah ada
        existing = db.query(SignalHistory).filter(
            SignalHistory.ticker == signal_data['ticker'],
            SignalHistory.date == signal_data['date']
        ).first()

        signal_code = signal_data.get('signal_code', '')
        close_price = signal_data.get('close', signal_data.get('close_price', 0))

        if existing:
            existing.close_price = close_price
            existing.signal_code = signal_code
            existing.signal_label = signal_data.get('signal_label', '')
            existing.reason = signal_data.get('reason', '')
        else:
            new_signal = SignalHistory(
                ticker=signal_data['ticker'],
                date=signal_data['date'],
                close_price=close_price,
                signal_code=signal_code,
                signal_label=signal_data.get('signal_label', ''),
                reason=signal_data.get('reason', '')
            )
            db.add(new_signal)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB ERROR] Gagal menyimpan {signal_data.get('ticker')}: {e}")
    finally:
        db.close()

def save_signals_to_db(signals_list: list):
    """Menyimpan banyak sinyal sekaligus dari list dictionary."""
    for sig in signals_list:
        save_signal_to_db(sig)

def get_latest_signals():
    """Mengambil seluruh sinyal saham paling baru dari database."""
    init_db()
    db: Session = SessionLocal()
    try:
        # Urutkan berdasarkan tanggal terbaru
        results = db.query(SignalHistory).order_by(SignalHistory.date.desc(), SignalHistory.id.desc()).all()
        
        # Filter unik per ticker (ambil tanggal paling baru)
        latest_dict = {}
        for row in results:
            if row.ticker not in latest_dict:
                latest_dict[row.ticker] = {
                    "ticker": row.ticker,
                    "date": row.date,
                    "close": row.close_price,
                    "signal_code": row.signal_code,
                    "signal_label": row.signal_label,
                    "reason": row.reason
                }
        return list(latest_dict.values())
    finally:
        db.close()