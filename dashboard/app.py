# dashboard/app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import os
import sys

# Tambahkan root directory ke sys.path agar modul src/ dapat di-import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.repository import get_latest_signals
from src.data.fetcher import fetch_stock_data
from src.data.indicators import add_technical_indicators
from dashboard.components.charts import plot_stock_chart

# ---------------------------------------------------------
# FUNGSI CACHING DATA (YAHOO FINANCE)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_fundamental_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception:
        return None

@st.cache_data(ttl=1800)
def fetch_ihsg_summary():
    try:
        ihsg = yf.Ticker("^JKSE")
        df = ihsg.history(period="1mo")
        if df.empty or len(df) < 2:
            return None
        
        latest_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change = latest_close - prev_close
        pct_change = (change / prev_close) * 100
        
        # Logika Sentimen Pasar berbasis MA-20
        ma20 = df['Close'].tail(20).mean()
        if latest_close > ma20 * 1.002:
            sentiment = "BULLISH"
            sentiment_color = "#34d399"
        elif latest_close < ma20 * 0.998:
            sentiment = "BEARISH"
            sentiment_color = "#f87171"
        else:
            sentiment = "SIDEWAYS"
            sentiment_color = "#fbbf24"
            
        return {
            "close": latest_close,
            "change": change,
            "pct_change": pct_change,
            "sentiment": sentiment,
            "sentiment_color": sentiment_color,
            "df_spark": df['Close'].tail(30)
        }
    except Exception:
        return None

# ---------------------------------------------------------
# FUNGSI MINI SPARKLINE CHART
# ---------------------------------------------------------
def create_sparkline(df_series, is_positive):
    line_color = "#34d399" if is_positive else "#f87171"
    fill_color = "rgba(52, 211, 153, 0.12)" if is_positive else "rgba(248, 113, 113, 0.12)"
    
    dates = [d.strftime('%d %b') if hasattr(d, 'strftime') else str(d) for d in df_series.index]
    values = df_series.values
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        fill='tozeroy',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5, shape='spline', smoothing=1.2),
        hoverinfo='text',
        text=[f"Tanggal: {d}<br>IHSG: <b>{v:,.2f}</b>" for d, v in zip(dates, values)]
    ))
    
    fig.add_trace(go.Scatter(
        x=[dates[-1]],
        y=[values[-1]],
        mode='markers',
        marker=dict(color=line_color, size=6),
        hoverinfo='none',
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(
            text="TREN IHSG (30 HARI)",
            font=dict(family="Inter, sans-serif", size=11, color="#94a3b8"),
            x=0.03,
            y=0.88
        ),
        margin=dict(l=8, r=8, t=30, b=8),
        height=82,
        paper_bgcolor='#1e293b',
        plot_bgcolor='#1e293b',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#0f172a',
            font_size=11,
            font_family="Inter, sans-serif",
            font_color='#f8fafc'
        )
    )
    return fig

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="StockPulse - Screener Saham IDX",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS (PREMIUM DARK THEME)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 1. Sembunyikan Navigasi Bawaan Streamlit */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 2. Background Aplikasi */
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

    /* 3. Branding Header Card di Sidebar dengan Logo SVG Professional */
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
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 4px;
        letter-spacing: 0.3px;
    }

    /* 4. Styling Streamlit Radio Buttons di Sidebar */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 6px !important;
    }

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

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-color: rgba(255, 255, 255, 0.05) !important;
        transform: translateX(2px);
    }

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

    /* 5. Footer Info Box di Sidebar */
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

    /* 6. Header Banner */
    .hero-container {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
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

    /* 8. PLOTLY SPARKLINE CONTAINER */
    div[data-testid="stPlotlyChart"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    /* 9. CUSTOM MODERN TABLE DESIGN */
    .custom-table-container {
        border: 1px solid #334155;
        border-radius: 10px;
        overflow: hidden;
        background-color: #1e293b;
        margin-top: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }
    .custom-table th {
        background-color: #0f172a;
        padding: 14px 18px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 1px solid #334155;
    }
    .custom-table td {
        padding: 12px 18px;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        vertical-align: middle;
    }
    .custom-table tr.table-row:hover {
        background-color: rgba(51, 65, 85, 0.4);
        transition: background-color 0.15s ease;
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }

    .custom-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-buy {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-wait {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-sell {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* 10. MULTISELECT FILTER TAGS */
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 2px 6px !important;
        min-height: 36px !important;
        align-items: center !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #475569 !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    [data-baseweb="tag"], 
    span[data-baseweb="tag"], 
    div[data-baseweb="tag"] {
        background-color: rgba(56, 189, 248, 0.12) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
        margin: 2px 3px !important;
        height: 26px !important;
        display: inline-flex !important;
        align-items: center !important;
    }

    [data-baseweb="tag"] span, 
    span[data-baseweb="tag"] span, 
    div[data-baseweb="tag"] span {
        color: #38bdf8 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        line-height: 1 !important;
    }

    [data-baseweb="tag"] svg, 
    span[data-baseweb="tag"] svg, 
    div[data-baseweb="tag"] svg,
    [data-baseweb="tag"] [data-baseweb="icon"] {
        fill: #64748b !important;
        color: #64748b !important;
        width: 14px !important;
        height: 14px !important;
    }
    [data-baseweb="tag"] svg:hover, 
    span[data-baseweb="tag"] svg:hover, 
    div[data-baseweb="tag"] svg:hover,
    [data-baseweb="tag"] [data-baseweb="icon"]:hover {
        fill: #f87171 !important;
        color: #f87171 !important;
    }

    div[data-testid="stWidgetLabel"] p {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 4px !important;
    }

    /* 11. COMPANY PROFILE CARD */
    .profile-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px 26px;
        margin-top: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .profile-header {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid rgba(51, 65, 85, 0.6);
        padding-bottom: 10px;
    }
    .profile-body {
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.7;
        text-align: justify;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNGSI RENDER TABEL MODERN HTML
# ---------------------------------------------------------
def render_modern_table(df):
    if df.empty:
        st.info("Tidak ada data sinyal yang sesuai dengan filter.")
        return

    rows_html = ""
    for _, row in df.iterrows():
        signal = str(row.get('signal_label', '')).upper()
        if "BUY" in signal:
            badge_class = "badge-buy"
            badge_text = "BUY NOW"
        elif "SELL" in signal or "AVOID" in signal:
            badge_class = "badge-sell"
            badge_text = "SELL / AVOID"
        else:
            badge_class = "badge-wait"
            badge_text = "WAIT"
        
        close_val = row.get('close', 0)
        formatted_price = f"Rp {close_val:,.0f}".replace(",", ".")
        
        rows_html += f'<tr class="table-row"><td style="color: #94a3b8; font-size: 0.85rem;">{row.get("date", "")}</td><td style="font-weight: 700; color: #38bdf8; font-size: 0.9rem;">{row.get("ticker", "")}</td><td style="font-weight: 600; color: #f8fafc; font-size: 0.88rem;">{formatted_price}</td><td><span class="custom-badge {badge_class}">{badge_text}</span></td><td style="color: #94a3b8; font-size: 0.82rem;">{row.get("reason", "")}</td></tr>'

    table_html = f'<div class="custom-table-container"><table class="custom-table"><thead><tr><th style="width: 15%;">TANGGAL</th><th style="width: 15%;">TICKER</th><th style="width: 20%;">HARGA</th><th style="width: 20%;">SINYAL ML</th><th style="width: 30%;">LOGIKA & GUARDRAILS</th></tr></thead><tbody>{rows_html}</tbody></table></div>'
    
    st.markdown(table_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    # Branding Header Card dengan Logo SVG Vector Modern
    st.markdown("""
        <div class="sidebar-brand-card">
            <div class="brand-title">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                <span>StockPulse</span>
            </div>
            <div class="brand-sub">IDX Quantitative Analytics Engine</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #475569; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; padding-left: 4px;'>MAIN MENU</p>", unsafe_allow_html=True)
    
    # Menu Navigasi Tanpa Emoji (SaaS Clean Style)
    menu = st.sidebar.radio(
        "",
        ["Screener Sinyal", "Detail Saham", "Analisa Fundamental"]
    )

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

# ---------------------------------------------------------
# 5. MARKET OVERVIEW BAR (IHSG WIDGET)
# ---------------------------------------------------------
ihsg_data = fetch_ihsg_summary()
if ihsg_data:
    is_pos = ihsg_data['change'] >= 0
    change_sign = "+" if is_pos else ""
    change_color = "#34d399" if is_pos else "#f87171"
    
    formatted_close = f"{ihsg_data['close']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_change_val = f"{ihsg_data['change']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    change_str = f"{change_sign}{formatted_change_val} ({change_sign}{ihsg_data['pct_change']:.2f}%)"

    col_i1, col_i2, col_i3 = st.columns([1.5, 1.2, 1.3])

    with col_i1:
        st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {change_color};">
                <div class="metric-label">Indeks Harga Saham Gabungan (IHSG)</div>
                <div style="display: flex; align-items: baseline; gap: 10px; margin-top: 4px;">
                    <span class="metric-value" style="color: #f8fafc; font-size: 1.55rem;">{formatted_close}</span>
                    <span style="color: {change_color}; font-weight: 700; font-size: 0.88rem;">{change_str}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_i2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Sentimen Pasar (MA-20)</div>
                <div style="margin-top: 8px;">
                    <span style="background-color: rgba(15, 23, 42, 0.8); border: 1px solid {ihsg_data['sentiment_color']}; color: {ihsg_data['sentiment_color']}; padding: 5px 14px; border-radius: 20px; font-weight: 700; font-size: 0.82rem;">
                        {ihsg_data['sentiment']}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_i3:
        fig_spark = create_sparkline(ihsg_data['df_spark'], is_pos)
        st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA SINYAL & KONTEN UTAMA
# ---------------------------------------------------------
signals = get_latest_signals()

if not signals:
    st.warning("Belum ada data di Database SQLite. Silakan jalankan pipeline `python run_fase4_test.py` terlebih dahulu.")
else:
    df_signals = pd.DataFrame(signals)

    # ---------------------------------------------------------
    # MENU 1: SCREENER SINYAL
    # ---------------------------------------------------------
    if menu == "Screener Sinyal":
        total_stocks = len(df_signals)
        buy_count = len(df_signals[df_signals['signal_label'] == "BUY NOW"])
        wait_count = len(df_signals[df_signals['signal_label'] == "WAIT"])
        sell_count = len(df_signals[df_signals['signal_label'] == "SELL / AVOID"])

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
                    <div class="metric-label">Sinyal BUY NOW</div>
                    <div class="metric-value">{buy_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
                <div class="metric-card card-wait">
                    <div class="metric-label">Sinyal WAIT</div>
                    <div class="metric-value">{wait_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
                <div class="metric-card card-sell">
                    <div class="metric-label">Sinyal SELL / AVOID</div>
                    <div class="metric-value">{sell_count}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_title, col_filter = st.columns([1.2, 1])

        with col_title:
            st.markdown("""
                <div style="padding-top: 4px;">
                    <h4 style="color: #f8fafc; font-weight: 700; margin: 0; font-size: 1.15rem;">Hasil Skrining Sinyal Harian</h4>
                    <p style="color: #64748b; font-size: 0.8rem; margin: 2px 0 0 0;">Daftar keputusan rekomendasi sinyal berdasarkan kuantitatif & guardrails</p>
                </div>
            """, unsafe_allow_html=True)

        with col_filter:
            selected_filter = st.multiselect(
                "Filter Sinyal Tampil:",
                options=["BUY NOW", "WAIT", "SELL / AVOID"],
                default=["BUY NOW", "WAIT", "SELL / AVOID"]
            )

        filtered_df = df_signals[df_signals['signal_label'].isin(selected_filter)]

        render_modern_table(filtered_df)

    # ---------------------------------------------------------
    # MENU 2: DETAIL SAHAM & GRAFIK
    # ---------------------------------------------------------
    elif menu == "Detail Saham":
        st.markdown("##### Grafik & Indikator Teknikal")
        
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
    elif menu == "Analisa Fundamental":
        st.markdown("##### Analisa Fundamental & Profil Perusahaan")
        
        selected_ticker = st.selectbox(
            "Pilih Saham:",
            options=df_signals['ticker'].tolist()
        )
        
        if selected_ticker:
            with st.spinner(f"Mengambil data fundamental {selected_ticker}..."):
                info = fetch_fundamental_info(selected_ticker)
                
                if info and info.get('shortName'):
                    long_name = info.get('longName', selected_ticker)
                    sector = info.get('sector', 'N/A')
                    industry = info.get('industry', 'N/A')
                    summary = info.get('longBusinessSummary', 'Deskripsi perusahaan tidak tersedia.')

                    st.markdown(f"""
                        <div class="hero-container" style="padding: 18px 22px; margin-bottom: 20px;">
                            <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc;">{long_name} ({selected_ticker})</div>
                            <div style="font-size: 0.85rem; color: #38bdf8; margin-top: 4px;">
                                Sektor: <b>{sector}</b> | Industri: <b>{industry}</b>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    mcap = info.get('marketCap')
                    if mcap and mcap >= 1e12:
                        mcap_str = f"Rp {mcap / 1e12:.2f} T"
                    elif mcap and mcap >= 1e9:
                        mcap_str = f"Rp {mcap / 1e9:.2f} M"
                    else:
                        mcap_str = "N/A"

                    per = f"{info.get('trailingPE'):.2f}x" if info.get('trailingPE') else "N/A"
                    pbv = f"{info.get('priceToBook'):.2f}x" if info.get('priceToBook') else "N/A"
                    roe = f"{info.get('returnOnEquity') * 100:.2f}%" if info.get('returnOnEquity') else "N/A"
                    div_yield = f"{info.get('dividendYield') * 100:.2f}%" if info.get('dividendYield') else "0.00%"
                    eps = f"Rp {info.get('trailingEps'):,.0f}" if info.get('trailingEps') else "N/A"
                    high_52 = f"Rp {info.get('fiftyTwoWeekHigh'):,.0f}" if info.get('fiftyTwoWeekHigh') else "N/A"
                    low_52 = f"Rp {info.get('fiftyTwoWeekLow'):,.0f}" if info.get('fiftyTwoWeekLow') else "N/A"

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Market Cap</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #38bdf8;">{mcap_str}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">PER (P/E Ratio)</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #f8fafc;">{per}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">PBV (P/B Ratio)</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #f8fafc;">{pbv}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">ROE (Return on Equity)</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #34d399;">{roe}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    c5, c6, c7, c8 = st.columns(4)
                    with c5:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Dividend Yield</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #fbbf24;">{div_yield}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c6:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">EPS (Laba / Lembar)</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #f8fafc;">{eps}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c7:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">52-Week High</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #f8fafc;">{high_52}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c8:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">52-Week Low</div>
                                <div class="metric-value" style="font-size: 1.4rem; color: #f8fafc;">{low_52}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown(f"""
                        <div class="profile-card">
                            <div class="profile-header">
                                Profil & Ringkasan Bisnis Perusahaan
                            </div>
                            <div class="profile-body">
                                {summary}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Gagal memuat data fundamental untuk **{selected_ticker}** dari Yahoo Finance.")