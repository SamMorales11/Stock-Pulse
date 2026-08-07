# dashboard/components/charts.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_stock_chart(df, ticker, show_volume=True, show_ma=True, show_bb=False, show_macd=True):
    """
    Membuat grafik Candlestick interaktif dengan Plotly Subplots berdasarkan toggle aktif.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Data saham tidak tersedia.")
        return fig

    # Tentukan susunan Subplot berdasarkan toggle aktif
    active_subcharts = []
    if show_volume:
        active_subcharts.append("volume")
    if show_macd:
        active_subcharts.append("macd")

    num_rows = 1 + len(active_subcharts)
    
    # Rasio tinggi row
    if num_rows == 3:
        row_heights = [0.60, 0.20, 0.20]
    elif num_rows == 2:
        row_heights = [0.75, 0.25]
    else:
        row_heights = [1.0]

    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights
    )

    dates = df.index

    # ---------------------------------------------------------
    # ROW 1: CANDLESTICK PRICE CHART
    # ---------------------------------------------------------
    fig.add_trace(go.Candlestick(
        x=dates,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Harga Close",
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ), row=1, col=1)

    # Moving Averages Overlay (MA20 & MA50)
    if show_ma:
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=dates, y=df['SMA_20'],
                mode='lines', name='MA 20',
                line=dict(color='#38bdf8', width=1.5)
            ), row=1, col=1)
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=dates, y=df['SMA_50'],
                mode='lines', name='MA 50',
                line=dict(color='#f59e0b', width=1.5)
            ), row=1, col=1)

    # Bollinger Bands Overlay
    if show_bb and all(col in df.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
        fig.add_trace(go.Scatter(
            x=dates, y=df['BB_Upper'],
            mode='lines', name='BB Upper',
            line=dict(color='rgba(148, 163, 184, 0.4)', width=1, dash='dash')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=dates, y=df['BB_Lower'],
            mode='lines', name='BB Lower',
            line=dict(color='rgba(148, 163, 184, 0.4)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(148, 163, 184, 0.05)'
        ), row=1, col=1)

    # ---------------------------------------------------------
    # ROW SUB-CHARTS (VOLUME & MACD)
    # ---------------------------------------------------------
    current_row = 2

    # Volume Sub-chart
    if show_volume and 'Volume' in df.columns:
        colors = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(
            x=dates, y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.8
        ), row=current_row, col=1)
        fig.update_yaxes(title_text="Vol", row=current_row, col=1, showgrid=False)
        current_row += 1

    # MACD Sub-chart
    if show_macd and all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Hist']):
        fig.add_trace(go.Scatter(
            x=dates, y=df['MACD'],
            mode='lines', name='MACD',
            line=dict(color='#38bdf8', width=1.5)
        ), row=current_row, col=1)
        
        fig.add_trace(go.Scatter(
            x=dates, y=df['MACD_Signal'],
            mode='lines', name='Signal',
            line=dict(color='#f59e0b', width=1.5)
        ), row=current_row, col=1)

        hist_colors = ['#10b981' if h >= 0 else '#ef4444' for h in df['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=dates, y=df['MACD_Hist'],
            name='Histogram',
            marker_color=hist_colors,
            opacity=0.6
        ), row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1, showgrid=False)

    # ---------------------------------------------------------
    # LAYOUT & THEME CONFIGURATION
    # ---------------------------------------------------------
    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> - Price Action & Technical Analysis",
            font=dict(family="Inter, sans-serif", size=16, color="#f8fafc"),
            x=0.01, y=0.98
        ),
        paper_bgcolor='#0b0f17',
        plot_bgcolor='#0f172a',
        font=dict(family="Inter, sans-serif", color='#94a3b8'),
        margin=dict(l=10, r=10, t=40, b=20),
        height=620,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11, color="#cbd5e1"),
            bgcolor="rgba(15, 23, 42, 0.8)"
        ),
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(
        gridcolor='#1e293b',
        zerolinecolor='#1e293b',
        showspikes=True,
        spikethickness=1,
        spikedash='dot',
        spikecolor='#475569'
    )
    fig.update_yaxes(
        gridcolor='#1e293b',
        zerolinecolor='#1e293b',
        showspikes=True,
        spikethickness=1,
        spikedash='dot',
        spikecolor='#475569'
    )

    return fig