import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import fetch_market_data, inject_custom_css

st.set_page_config(page_title="Asset Explorer — QuantX", page_icon="📊", layout="wide")
inject_custom_css()

df_prices = fetch_market_data()

st.title("Granular Asset Analysis & Risk Metrics")
st.caption(
    "Evaluate historical price action, moving-average indicators, and tail-risk"
    " statistics[cite: 1, 2]."
)

selected_asset = st.selectbox(
    "Select Target Asset", ["Gold", "Bitcoin", "NVIDIA"]
)
asset_series = df_prices[selected_asset]

tab_chart, tab_risk, tab_returns = st.tabs(
    ["📈 Price & Technical Indicators", "🛡️ Risk Metrics", "📊 Return Distribution"]
)

with tab_chart:
  c1, c2 = st.columns([3, 1])
  with c2:
    show_sma20 = st.checkbox("Show SMA 20", value=True)
    show_sma50 = st.checkbox("Show SMA 50", value=True)
    show_ema20 = st.checkbox("Show EMA 20", value=True)

  sma_20 = asset_series.rolling(window=20).mean()
  sma_50 = asset_series.rolling(window=50).mean()
  ema_20 = asset_series.ewm(span=20, adjust=False).mean()

  fig = go.Figure()
  fig.add_trace(
      go.Scatter(
          x=asset_series.index,
          y=asset_series,
          name="Spot Price",
          line=dict(color="#3b82f6", width=2),
      )
  )
  if show_sma20:
    fig.add_trace(
        go.Scatter(
            x=sma_20.index,
            y=sma_20,
            name="SMA 20",
            line=dict(color="#f59e0b", dash="dash"),
        )
    )
  if show_sma50:
    fig.add_trace(
        go.Scatter(
            x=sma_50.index,
            y=sma_50,
            name="SMA 50",
            line=dict(color="#ef4444", dash="dash"),
        )
    )
  if show_ema20:
    fig.add_trace(
        go.Scatter(
            x=ema_20.index,
            y=ema_20,
            name="EMA 20",
            line=dict(color="#10b981"),
        )
    )

  fig.update_layout(
      title=f"{selected_asset} Technical Overlay",
      template="plotly_dark",
      height=450,
      hovermode="x unified",
  )
  st.plotly_chart(fig, use_container_width=True)

with tab_risk:
  daily_rets = asset_series.pct_change().dropna()
  ann_vol = daily_rets.std() * np.sqrt(252) * 100
  cum_ret = (
      (asset_series.iloc[-1] - asset_series.iloc[0]) / asset_series.iloc[0]
  ) * 100
  sharpe = (daily_rets.mean() * 252) / (daily_rets.std() * np.sqrt(252))
  rolling_max = asset_series.cummax()
  drawdown = (asset_series - rolling_max) / rolling_max
  max_dd = drawdown.min() * 100

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Cumulative Return", f"{cum_ret:.2f}%")
  c2.metric("Annualized Volatility", f"{ann_vol:.2f}%")
  c3.metric("Sharpe Ratio (Rf=0)", f"{sharpe:.2f}")
  c4.metric("Maximum Drawdown", f"{max_dd:.2f}%")

  fig_dd = px.area(
      drawdown * 100,
      title=f"{selected_asset} Historical Drawdown (%)",
      template="plotly_dark",
  )
  fig_dd.update_layout(height=300)
  st.plotly_chart(fig_dd, use_container_width=True)

with tab_returns:
  fig_hist = px.histogram(
      daily_rets * 100,
      nbins=100,
      title=f"{selected_asset} Daily Return Distribution (%)",
      template="plotly_dark",
  )
  fig_hist.update_layout(height=400)
  st.plotly_chart(fig_hist, use_container_width=True)