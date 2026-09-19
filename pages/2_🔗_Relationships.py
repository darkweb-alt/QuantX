import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import fetch_market_data, inject_custom_css

st.set_page_config(
    page_title="Cross-Asset Intelligence — QuantX", page_icon="🔗", layout="wide"
)
inject_custom_css()

df_prices = fetch_market_data()
returns_df = df_prices.pct_change().dropna()

st.title("Cross-Asset Intelligence & Relationship Explorer")
st.caption(
    "Analyze static correlation matrices, time-varying rolling correlations, and"
    " lead-lag association metrics[cite: 1, 2]."
)

tab_corr, tab_roll, tab_leadlag = st.tabs(
    ["Correlation Matrix", "Rolling Correlation", "Lead-Lag Explorer"]
)

with tab_corr:
  st.subheader("Static Correlation Matrix")
  corr_matrix = returns_df.corr()
  fig = px.imshow(
      corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1
  )
  fig.update_layout(template="plotly_dark", height=420)
  st.plotly_chart(fig, use_container_width=True)

with tab_roll:
  st.subheader("Dynamic Rolling Correlation")
  c1, c2, c3 = st.columns(3)
  asset_a = c1.selectbox("Asset A", ["Bitcoin", "Gold", "NVIDIA"], key="roll_a")
  asset_b = c2.selectbox("Asset B", ["NVIDIA", "Gold", "Bitcoin"], key="roll_b")
  window = c3.slider("Rolling Window (Days)", 15, 120, 30)

  rolling_corr = (
      returns_df[asset_a].rolling(window).corr(returns_df[asset_b]).dropna()
  )
  fig_roll = px.line(
      rolling_corr,
      title=f"{window}-Day Rolling Correlation ({asset_a} vs {asset_b})",
      template="plotly_dark",
  )
  fig_roll.update_layout(height=400)
  st.plotly_chart(fig_roll, use_container_width=True)

with tab_leadlag:
  st.subheader("Lead-Lag Association Study")
  c1, c2 = st.columns(2)
  lead_asset = c1.selectbox("Leading Asset", ["Bitcoin", "NVIDIA", "Gold"])
  lag_asset = c2.selectbox(
      "Lagging Asset", ["NVIDIA", "Gold", "Bitcoin"], index=1
  )
  lag_days = st.slider("Select Lag Window (Days)", 1, 5, 1)

  lag_corr = (
      returns_df[lead_asset]
      .shift(lag_days)
      .corr(returns_df[lag_asset])
  )

  st.metric(
      label=(
          f"Cross-Correlation Coefficient ({lead_asset} t-{lag_days} →"
          f" {lag_asset} t)"
      ),
      value=f"{lag_corr:.4f}",
  )
  st.info(
      "📌 **Methodological Disclaimer:** Correlation does not establish"
      " causation. Lead-lag associations are displayed for statistical"
      " discovery and feature engineering only[cite: 1, 2]."
  )