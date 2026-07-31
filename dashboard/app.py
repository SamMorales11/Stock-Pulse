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
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="StockPulse - Screener Saham IDX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS (PREMIUM DARK SIDEBAR & DASHBOARD)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Import Font Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 1. Sembunyikan Navigasi Bawaan Streamlit */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 2. Style Background Utama & Sidebar */
    .main {
        background-color: #0b0f17;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d131f !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }

    /* 3. Branding Header Card di Sidebar */
    .sidebar-brand-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .brand-title {
        color: #38bdf8;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 2px;
        letter-spacing: 0.3px;
    }

    /* 4. MERAPIKAN STREAMLIT RADIO BUTTON PADA SIDEBAR */
    /* Hapus Label Judul Radio */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    
    /* Gap Antar Item Menu */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 6px !important;
    }

    /* Style Item Menu Pasif */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        color: #94a3b8 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
    }

    /* HAPUS TOTAL LINGKARAN RADIO BUTTON (CIRCLE DOTS) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
    }

    /* Efek Hover Menu */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-color: rgba(255, 255, 255, 0.05) !important;
        transform: translateX(2px);
    }

    /* Style Item Menu AKTIF (Glow & Left Active Border) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.15) 0%, rgba(56, 189, 248, 0.03) 100%) !important;
        color: #38bdf8 !important;
        font-weight: 600 !important;
        border-left: 3px solid #38bdf8 !important;
        border-top: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-top-left-radius: 2px !important;
        border-bottom-left-radius: 2px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    /* 5. Footer Info Box di Bawah Sidebar */
    .sidebar-footer {
        margin-top: 2.5rem;
        padding: 12px;
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid #1e293b;
        border-radius: 8px;
        font-size: 0.72rem;
        color: #64748b;
    }
    .status-dot {
        height: 6px;
        width: 6px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }

    /* 6. Header Banner Utama */
    .hero-container {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 0.875rem;
        color: #94a3b8;
        margin: 0;
    }
    .badge-status {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-size: 0.72rem;
        padding: 3px 8px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* 7. Metric Cards Design */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        border-color: #475569;
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1;
    }
    
    .card-total .metric-value { color: #f8fafc; }
    .card-buy { border-top: 3px solid #10b981; }
    .card-buy .metric-value { color: #34d399; }
    .card-wait { border-top: 3px solid #f59e0b; }
    .card-wait .metric-value { color: #fbbf24; }
    .card-sell { border-top: 3px solid #ef4444; }
    .card-sell .metric-value { color: #f87171; }

    /* Custom Table Container */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    # Branding Card
    st.markdown("""
        <div class="sidebar-brand-card">
            <div class="brand-title">⚡ StockPulse</div>
            <div class="brand-sub">IDX Quantitative Analytics Engine</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Subheader Navigasi
    st.markdown("<p style='color: #475569; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; padding-left: 4px;'>MAIN MENU</p>", unsafe_allow_html=True)
    
    # Menu Navigasi Berbentuk Tab Modern
    menu = st.sidebar.radio(
        "",
        ["📋  Screener Sinyal", "📈  Detail Saham", "📊  Analisa Fundamental"]
    )

    # Footer Status Widget di Bawah Sidebar
    st.markdown("""
        <div class="sidebar-footer">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: 600; color: #94a3b8;"><span class="status-dot"></span>Engine Status</span>
                <span style="color: #34d399; font-weight: 600;">Active</span>
            </div>
            <div>Database: SQLite (IDX Data)</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. HERO HEADER SECTION
# ---------------------------------------------------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">
            StockPulse Analytics
            <span class="badge-status">LIVE SYSTEM</span>
        </div>
        <p class="hero-subtitle">
            Sistem Skrining & Prediksi Keputusan Harian Saham IDX Berbasis Machine Learning
        </p>
    </div>
""", unsafe_allow_html=True)

# Load Sinyal Terbaru dari SQLite Database
signals = get_latest_signals()

if not signals:
    st.warning("⚠️ Belum ada data di Database SQLite. Silakan jalankan pipeline `python run_fase4_test.py` terlebih dahulu.")
else:
    df_signals = pd.DataFrame(signals)

    # ---------------------------------------------------------
    # MENU 1: SCREENER SINYAL
    # ---------------------------------------------------------
    if "Screener Sinyal" in menu:
        total_stocks = len(df_signals)
        buy_count = len(df_signals[df_signals['signal_label'] == "BUY NOW"])
        wait_count = len(df_signals[df_signals['signal_label'] == "WAIT"])
        sell_count = len(df_signals[df_signals['signal_label'] == "SELL / AVOID"])

        # Metric Cards Layout
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
                <div class="metric-card card-total">
                    <div class="metric-label">Total Teranalisa</div>
                    <div class="metric-value">{total_stocks}</div>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
                <div class="metric-card card-buy">
                    <div class="metric-label">Sinyal BUY NOW 🟢</div>
                    <div class="metric-value">{buy_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
                <div class="metric-card card-wait">
                    <div class="metric-label">Sinyal WAIT 🟡</div>
                    <div class="metric-value">{wait_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
                <div class="metric-card card-sell">
                    <div class="metric-label">Sinyal SELL / AVOID 🔴</div>
                    <div class="metric-value">{sell_count}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabel Filter & Data
        st.markdown("##### 📋 Hasil Skrining Sinyal")

        selected_filter = st.multiselect(
            "Filter Sinyal:",
            options=["BUY NOW", "WAIT", "SELL / AVOID"],
            default=["BUY NOW", "WAIT", "SELL / AVOID"]
        )

        filtered_df = df_signals[df_signals['signal_label'].isin(selected_filter)]

        st.dataframe(
            filtered_df[['date', 'ticker', 'close', 'signal_label', 'reason']],
            column_config={
                "date": "Tanggal",
                "ticker": "Ticker",
                "close": st.column_config.NumberColumn("Harga (Rp)", format="Rp %'d"),
                "signal_label": "Sinyal ML",
                "reason": "Logika & Guardrails"
            },
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------------------
    # MENU 2: DETAIL SAHAM & GRAFIK
    # ---------------------------------------------------------
    elif "Detail Saham" in menu:
        st.markdown("##### 🔍 Grafik & Indikator Teknikal")
        
        selected_ticker = st.selectbox(
            "Pilih Saham:",
            options=df_signals['ticker'].tolist()
        )

        if selected_ticker:
            with st.spinner(f"Memuat data {selected_ticker}..."):
                df_stock = fetch_stock_data(selected_ticker, period="1y")
                if not df_stock.empty:
                    df_ind = add_technical_indicators(df_stock)
                    fig = plot_stock_chart(df_ind, selected_ticker)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Gagal memuat data grafik saham.")

    # ---------------------------------------------------------
    # MENU 3: ANALISA FUNDAMENTAL
    # ---------------------------------------------------------
    elif "Analisa Fundamental" in menu:
        st.markdown("##### 📊 Analisa Fundamental Saham")
        
        selected_ticker = st.selectbox(
            "Pilih Saham:",
            options=df_signals['ticker'].tolist()
        )
        
        st.info(f"Modul Analisa Fundamental untuk **{selected_ticker}** siap dihubungkan dengan data laporan keuangan.")