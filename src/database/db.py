# src/database/db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

os.makedirs("data", exist_ok=True)
DATABASE_URL = "sqlite:///data/database.sqlite"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    date = Column(String)
    close_price = Column(Float)
    signal_code = Column(Integer)
    signal_label = Column(String)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Membuat tabel database jika belum ada."""
    Base.metadata.create_all(bind=engine)