# ⚡ StockPulse Analytics

**IDX Quantitative Analytics Engine & Machine Learning Screener**

StockPulse adalah platform analitik kuantitatif dan skrining saham berbasis *Machine Learning* yang dirancang khusus untuk pasar saham Indonesia (IDX). Platform ini menyajikan sinyal keputusan harian (*BUY NOW*, *WAIT*, *SELL / AVOID*), pemantauan sentimen makro pasar, grafik teknikal interaktif, kalkulator *Risk & Money Management*, serta analisis fundamental perusahaan secara *real-time*.

---

## 📸 Preview Dashboard

### 1. Market Overview & Screener Sinyal Harian
<img width="980" height="521" alt="Screenshot 2026-08-11 081540" src="https://github.com/user-attachments/assets/1498a7a2-dda7-46b0-aa69-97fa683b682f" />
<img width="986" height="585" alt="Screenshot 2026-08-11 081552" src="https://github.com/user-attachments/assets/c39ba936-fc9a-4277-99e5-9e6d81ff21c3" />
*Tampilan utama mencakup widget IHSG, performa sektor harian (IDX Sector Breadth), metric cards sinyal, dan tabel rekomendasi.*

### 2. Grafik Teknikal Interaktif & Indicator Toggle
<img width="994" height="183" alt="Screenshot 2026-08-11 081712" src="https://github.com/user-attachments/assets/2dcd3d52-fd8a-40e0-bef1-fb53ed4a08b5" />
<img width="991" height="588" alt="Screenshot 2026-08-11 081728" src="https://github.com/user-attachments/assets/d53dc11a-8773-41f8-bcc5-a9c2178637c1" />
*Grafik Candlestick interaktif dengan switcher timeframe (1M, 3M, 6M, 1Y, YTD) serta opsi toggle untuk Volume, MA20/50, Bollinger Bands, dan MACD.*

### 3. Kalkulator Position Sizing & Risk Management
![Risk Calculator](docs/screenshots/risk_calculator.png)
*Fitur kalkulator terintegrasi untuk menghitung jumlah lot maksimal, total alokasi modal, batas stop loss, dan Risk/Reward Ratio secara objektif.*

### 4. Analisa Fundamental & Profil Perusahaan
![Fundamental Analysis](docs/screenshots/fundamental.png)
*Ringkasan indikator keuangan utama (Market Cap, PER, PBV, ROE, Dividend Yield, EPS) beserta profil ringkasan bisnis perusahaan.*

---

## ✨ Fitur Utama

- **Makro Pasar & Sector Breadth**:
  - Ringkasan indeks IHSG (`^JKSE`) dengan indikator sentimen otomatis berbasis Moving Average 20 harian.
  - *Sparkline chart* tren IHSG 30 hari tanpa beban visual.
  - Performa harian 5 sektor utama IDX (Finansial, Energi, Konsumer, Teknologi & Telko, Tambang & Industri).
- **Automated ML Screener**:
  - Rekomendasi sinyal kuantitatif yang divalidasi oleh *Guardrails* teknikal (RSI, SMA, Overbought/Oversold).
  - Filter multi-pilihan modern untuk mengisolasi sinyal *BUY*, *WAIT*, atau *SELL*.
- **Interactive Technical Analysis**:
  - Plotly Candlestick subplots yang tersinkronisasi (*Shared X-Axis*).
  - Switcher timeframe cepat (`1M`, `3M`, `6M`, `1Y`, `YTD`).
  - Toggle dinamis untuk mengaktifkan/menonaktifkan *Volume*, *MA 20/50*, *Bollinger Bands*, dan *MACD*.
- **Kalkulator Risk & Position Sizing**:
  - Simulasi alokasi modal trading berdasarkan toleransi risiko per *trade* (%).
  - Perhitungan jumlah lot aman, toleransi kerugian nominal, dan proyeksi *Risk/Reward Ratio*.
- **Fundamental & Corporate Profile**:
  - Metrik fundamental esensial dari Yahoo Finance API.
  - *Company Profile Card* yang ringkas dan nyaman dibaca.

---

## 🛠️ Teknologi yang Digunakan

- **Language**: Python 3.10+
- **Frontend / Dashboard**: Streamlit (Custom CSS Dark Slate Fintech Theme)
- **Data Visualization**: Plotly (Graph Objects & Subplots)
- **Data Source**: `yfinance` (Yahoo Finance API)
- **Database & ORM**: SQLite & SQLAlchemy
- **Data Processing**: Pandas, NumPy

---

## 📁 Struktur Folder Project

```text
StockPulse/
├── dashboard/
│   ├── components/
│   │   └── charts.py       # Pembuat grafik Plotly interaktif & subplots
│   └── app.py              # File utama aplikasi Streamlit
├── data/
│   └── database.sqlite     # Database SQLite penyimpanan sinyal
├── src/
│   ├── data/
│   │   ├── fetcher.py      # Module pengambil data pasar
│   │   └── indicators.py   # Penghitung indikator teknikal (RSI, MA, BB, MACD)
│   └── database/
│       ├── db.py           # Inisialisasi SQLAlchemy Session & Model
│       └── repository.py   # Fungsi CRUD database
├── docs/
│   └── screenshots/        # Folder simpan gambar screenshot README
├── run_fase4_test.py       # Pipeline pemrosesan sinyal ML & update DB
├── requirements.txt        # Daftar dependensi library Python
└── README.md
```

## 🚀 Cara Menjalankan Project

## 1. Clone Repository
```text
git clone [https://github.com/UsernameKamu/StockPulse.git](https://github.com/UsernameKamu/StockPulse.git)
cd StockPulse
```
## 2. Aktifkan Virtual Environment & Install Dependensi
```text
# Untuk Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependensi
pip install -r requirements.txt
```
## 3. Jalankan Pipeline Pembaruan Sinyal
```text
python run_fase4_test.py
```
## 4. Jalankan Dashboard Streamlit
```text
streamlit run dashboard/app.py
```
