# dashboard/app.py
import streamlit as st
import pandas as pd
import os
import sys

# Tambahkan root directory ke sys.path agar modul src/ dapat di-import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.repository import get_latest_signals
from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators
from dashboard.components.charts import plot_stock_chart

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="StockPulse - Dashboard Sinyal Saham IDX",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS UNTUK MERAPIKAN UI & SIDEBAR MENU
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Sembunyikan Navigasi Otomatis Streamlit (Penyebab Menu Ganda) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 2. Styling Background Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        padding-top: 1rem;
    }

    /* 3. Menghilangkan Lingkaran Radio Button & Mengubah Pilihan Menjadi Tombol Modern */
    div[data-testid="stRadio"] > label {
        display: none;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }

    div[data-testid="stRadio"] > div > label {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        color: #94a3b8;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        display: flex;
        align-items: center;
        width: 100%;
    }

    /* Efek saat kursor diarahkan (Hover) */
    div[data-testid="stRadio"] > div > label:hover {
        background-color: #334155;
        color: #f8fafc;
        border-color: #3b82f6;
    }

    /* Hilangkan titik bulat radio button */
    div[data-testid="stRadio"] > div > label > div:first-child {
        display: none !important;
    }

    /* Highlight untuk menu yang sedang aktif */
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        color: #60a5fa !important;
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* 4. Formatting Card Metric */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <h2 style="color: #38bdf8; margin: 0; font-size: 1.6rem;">📈 StockPulse</h2>
            <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">AI/ML Stock Screener IDX</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Menu Utama</p>", unsafe_allow_html=True)
    
    # Menu Navigasi Berbentuk Tombol
    menu = st.sidebar.radio(
        "",
        ["📋  Screener Sinyal", "📈  Detail Saham", "📊  Analisa Fundamental"]
    )

# ---------------------------------------------------------
# 4. HEADER APLIKASI
# ---------------------------------------------------------
st.title("📈 StockPulse: AI/ML Stock Screener IDX")
st.caption("Platform Analisa & Prediksi Sinyal Keputusan Harian Saham Indonesia berbasis Machine Learning")
st.divider()

# Load Sinyal Terbaru dari SQLite Database
signals = get_latest_signals()

if not signals:
    st.warning("⚠️ Belum ada data di Database SQLite. Silakan jalankan pipeline `python run_fase4_test.py` terlebih dahulu.")
else:
    df_signals = pd.DataFrame(signals)

    # ---------------------------------------------------------
    # HALAMAN 1: SCREENER SINYAL
    # ---------------------------------------------------------
    if "Screener Sinyal" in menu:
        st.subheader("📋 Ringkasan & Tabel Prediksi Sinyal Harian")

        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        total_stocks = len(df_signals)
        buy_count = len(df_signals[df_signals['signal_label'] == "BUY NOW"])
        wait_count = len(df_signals[df_signals['signal_label'] == "WAIT"])
        sell_count = len(df_signals[df_signals['signal_label'] == "SELL / AVOID"])

        col1.metric("Total Saham Teranalisa", total_stocks)
        col2.metric("🟢 Sinyal BUY NOW", buy_count)
        col3.metric("🟡 Sinyal WAIT", wait_count)
        col4.metric("🔴 Sinyal SELL / AVOID", sell_count)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filter & Tabel Dataframe
        selected_filter = st.multiselect(
            "Filter Berdasarkan Keputusan Sinyal:",
            options=["BUY NOW", "WAIT", "SELL / AVOID"],
            default=["BUY NOW", "WAIT", "SELL / AVOID"]
        )

        filtered_df = df_signals[df_signals['signal_label'].isin(selected_filter)]

        st.dataframe(
            filtered_df[['date', 'ticker', 'close', 'signal_label', 'reason']],
            column_config={
                "date": "Tanggal",
                "ticker": "Kode Saham",
                "close": st.column_config.NumberColumn("Harga Terakhir (Rp)", format="Rp %'d"),
                "signal_label": "Sinyal ML",
                "reason": "Catatan Logika & Guardrails"
            },
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------------------
    # HALAMAN 2: DETAIL SAHAM & GRAFIK
    # ---------------------------------------------------------
    elif "Detail Saham" in menu:
        st.subheader("🔍 Visualisasi Grafik & Indikator Teknikal")
        
        selected_ticker = st.selectbox(
            "Pilih Saham untuk Menganalisa Grafik Lengkap:",
            options=df_signals['ticker'].tolist()
        )

        if selected_ticker:
            with st.spinner(f"Memuat data & grafik {selected_ticker}..."):
                df_stock = fetch_stock_data(selected_ticker, period="1y")
                if not df_stock.empty:
                    df_ind = add_technical_indicators(df_stock)
                    fig = plot_stock_chart(df_ind, selected_ticker)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Gagal memuat data grafik saham.")

    # ---------------------------------------------------------
    # HALAMAN 3: ANALISA FUNDAMENTAL
    # ---------------------------------------------------------
    elif "Analisa Fundamental" in menu:
        st.subheader("📊 Analisa Fundamental Saham")
        
        selected_ticker = st.selectbox(
            "Pilih Saham untuk Melihat Rasio Fundamental:",
            options=df_signals['ticker'].tolist()
        )
        
        st.info(f"Halaman Analisa Fundamental untuk **{selected_ticker}** siap dihubungkan dengan data laporan keuangan (PER, PBV, ROE, Dividend Yield).")