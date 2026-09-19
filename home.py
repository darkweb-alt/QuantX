import plotly.express as px
import streamlit as st
from utils import fetch_market_data, inject_custom_css

st.set_page_config(
    page_title="QuantX — Multi-Asset Financial Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
df_prices = fetch_market_data()

# Sidebar Command Panel
st.sidebar.title("⚡ QUANTX TERMINAL")
st.sidebar.caption("Institutional Quantitative Intelligence")
st.sidebar.markdown(
    """
<div class="live-indicator">
    <div class="pulsing-dot"></div>
    SYSTEM LIVE & SECURE
</div>
""",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "📡 **Data Pipeline:** `Yahoo Finance Real-Time`\n\n🛡️ **Risk Model:**"
    " `Active (VaR / Drawdown)`"
)
st.sidebar.markdown("**Active Universe:** Gold • Bitcoin • NVIDIA[cite: 1, 2]")

# Hero Header Section
st.markdown(
    """
<div style="padding: 10px 0px 20px 0px;">
    <h1 style="font-size: 3rem; background: linear-gradient(to right, #60a5fa, #3b82f6, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        QuantX Intelligence Engine
    </h1>
    <p style="font-size: 1.25rem; color: #94a3b8; max-width: 800px;">
        Institutional multi-asset analytics, dynamic correlation intelligence, regime-adaptive backtesting, and automated robustness stress-testing[cite: 1, 2].
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Top Live Metric Snapshot Cards
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
  gold_ret = (
      (df_prices["Gold"].iloc[-1] - df_prices["Gold"].iloc[0])
      / df_prices["Gold"].iloc[0]
  ) * 100
  st.markdown(
      f"""
    <div class="glass-card">
        <h4 style="margin:0; color: #f1f5f9;">🟡 Gold (MCX Futures)</h4>
        <h2 style="margin: 10px 0 5px 0; color: #f8fafc;">₹{df_prices['Gold'].iloc[-1]:,.2f}</h2>
        <span style="color: {'#34d399' if gold_ret >= 0 else '#ef4444'}; font-weight: 600;">{gold_ret:+.2f}% Cumulative Return</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col2:
  btc_ret = (
      (df_prices["Bitcoin"].iloc[-1] - df_prices["Bitcoin"].iloc[0])
      / df_prices["Bitcoin"].iloc[0]
  ) * 100
  st.markdown(
      f"""
    <div class="glass-card">
        <h4 style="margin:0; color: #f1f5f9;">₿ Bitcoin (BTC-USD)</h4>
        <h2 style="margin: 10px 0 5px 0; color: #f8fafc;">₹{df_prices['Bitcoin'].iloc[-1]:,.2f}</h2>
        <span style="color: {'#34d399' if btc_ret >= 0 else '#ef4444'}; font-weight: 600;">{btc_ret:+.2f}% Cumulative Return</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col3:
  nvda_ret = (
      (df_prices["NVIDIA"].iloc[-1] - df_prices["NVIDIA"].iloc[0])
      / df_prices["NVIDIA"].iloc[0]
  ) * 100
  st.markdown(
      f"""
    <div class="glass-card">
        <h4 style="margin:0; color: #f1f5f9;">🟢 NVIDIA (NVDA)</h4>
        <h2 style="margin: 10px 0 5px 0; color: #f8fafc;">₹{df_prices['NVIDIA'].iloc[-1]:,.2f}</h2>
        <span style="color: {'#34d399' if nvda_ret >= 0 else '#ef4444'}; font-weight: 600;">{nvda_ret:+.2f}% Cumulative Return</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

# Main Intelligence Chart Container
st.markdown("### 📈 Cross-Asset Normalized Growth Trajectory (Base Index = 100)")
normalized_df = df_prices / df_prices.iloc[0] * 100

fig = px.line(
    normalized_df,
    labels={"value": "Normalized Index Value", "index": "Trading Date"},
    template="plotly_dark",
)
fig.update_layout(
    height=440,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color="#f1f5f9"),
    ),
)
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.05)")
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.05)")

st.plotly_chart(fig, use_container_width=True)

# Quick Navigation Guide for Judges
st.markdown("---")
st.markdown("### 🚀 Platform Module Directory")
col_a, col_b, col_c = st.columns(3, gap="medium")

with col_a:
  st.markdown(
      """
    <div class="glass-card">
        <h4 style="color: #60a5fa;">📊 Asset Explorer</h4>
        <p>Inspect spot prices, rolling moving averages (SMA/EMA), drawdown depths, and return distributions[cite: 1, 2].</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col_b:
  st.markdown(
      """
    <div class="glass-card">
        <h4 style="color: #60a5fa;">🔗 Relationship Lab</h4>
        <p>Audit static correlation matrices, time-varying rolling correlations, and lead-lag directional associations[cite: 1, 2].</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col_c:
  st.markdown(
      """
    <div class="glass-card">
        <h4 style="color: #60a5fa;">🧪 Stress & Strategy Lab</h4>
        <p>Simulate portfolio strategies with transaction friction and stress-test parameter sensitivity via heatmaps[cite: 1, 2].</p>
    </div>
    """,
      unsafe_allow_html=True,
  )