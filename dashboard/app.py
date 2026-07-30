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

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="StockPulse - Dashboard Sinyal Saham IDX",
    page_icon="📈",
    layout="wide"
)

st.title("📈 StockPulse: AI/ML Stock Screener IDX")
st.caption("Platform Analisa & Prediksi Sinyal Keputusan Harian Saham Indonesia berbasis Machine Learning")

# Load Sinyal Terbaru dari SQLite Database
signals = get_latest_signals()

if not signals:
    st.warning("⚠️ Belum ada data di Database SQLite. Silakan jalankan pipeline `python run_fase4_test.py` terlebih dahulu.")
else:
    df_signals = pd.DataFrame(signals)

    # 1. Ringkasan Metrik (Metric Cards)
    col1, col2, col3, col4 = st.columns(4)
    total_stocks = len(df_signals)
    buy_count = len(df_signals[df_signals['signal_label'] == "BUY NOW"])
    wait_count = len(df_signals[df_signals['signal_label'] == "WAIT"])
    sell_count = len(df_signals[df_signals['signal_label'] == "SELL / AVOID"])

    col1.metric("Total Saham Teranalisa", total_stocks)
    col2.metric("🟢 Sinyal BUY NOW", buy_count)
    col3.metric("🟡 Sinyal WAIT", wait_count)
    col4.metric("🔴 Sinyal SELL / AVOID", sell_count)

    st.divider()

    # 2. Tabel Screener dengan Filter
    st.subheader("📋 Screener Hasil Prediksi Harian")
    
    selected_filter = st.multiselect(
        "Filter Berdasarkan Keputusan Sinyal:",
        options=["BUY NOW", "WAIT", "SELL / AVOID"],
        default=["BUY NOW", "WAIT", "SELL / AVOID"]
    )

    filtered_df = df_signals[df_signals['signal_label'].isin(selected_filter)]

    # Format Tampilan Tabel
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

    st.divider()

    # 3. Visualisasi Grafik Detail Per Saham
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