# dashboard/components/charts.py
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_stock_chart(df: pd.DataFrame, ticker: str):
    """Membuat grafik Candlestick interaktif + Indikator Teknikal (SMA & RSI)."""
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        subplot_titles=(f'Grafik Pergerakan Harga: {ticker}', 'RSI (14)'),
        row_heights=[0.7, 0.3]
    )

    # 1. Grafik Candlestick
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Harga'
    ), row=1, col=1)

    # 2. Moving Averages
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], line=dict(color='orange', width=1.2), name='SMA 20'), row=1, col=1)
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], line=dict(color='cyan', width=1.2), name='SMA 50'), row=1, col=1)

    # 3. Indikator RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_dark"
    )
    return fig