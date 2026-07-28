# config/settings.py
import os

# Daftar sampel ticker IDX awal (Bisa diperluas ke seluruh emiten)
DEFAULT_TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK",
    "GOTO.JK", "ICBP.JK", "UNVR.JK", "AMRT.JK", "ADRO.JK",
    "BBNI.JK", "CPIN.JK", "KLBF.JK", "PGAS.JK", "PTBA.JK"
]

# Minimum rata-rata nilai transaksi harian (IDR) untuk lolos filter likuiditas
MIN_DAILY_TRANSACTION_VALUE = 500_000_000  # Rp 500 Juta

# Periode hari untuk kalkulasi rata-rata likuiditas
LIQUIDITY_CHECK_DAYS = 20

# Parameter penarikan data yfinance
DEFAULT_PERIOD = "1y"   # Data historis 1 tahun terakhir
DEFAULT_INTERVAL = "1d" # Interval harian