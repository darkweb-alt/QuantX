import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import fetch_market_data, inject_custom_css

st.set_page_config(
    page_title="Advanced Quant Lab — QuantX", page_icon="🚀", layout="wide"
)
inject_custom_css()

df_prices = fetch_market_data()
returns_df = df_prices.pct_change().dropna()

st.title("🚀 Advanced Quantitative Lab & Portfolio Optimizer")
st.markdown(
    "Executing institutional-grade Monte Carlo simulations, Markowitz mean-variance"
    " portfolio optimization, and Value at Risk (VaR) telemetry."
)
st.markdown("---")

# Navigation Tabs for Advanced Features
tab_mc, tab_opt, tab_var = st.tabs(
    [
        "🎲 Monte Carlo Future Simulation",
        "📊 Portfolio Weight Optimizer",
        "⚠️ Value at Risk (VaR) & Tail Risk",
    ]
)

# --- TAB 1: MONTE CARLO SIMULATION ---
with tab_mc:
  st.subheader("Monte Carlo Price Path Simulation (Geometric Brownian Motion)")
  st.markdown(
      "Simulate 250 future trading paths based on historical drift and volatility"
      " parameters."
  )

  col1, col2 = st.columns([1, 2.5], gap="large")

  with col1:
    mc_asset = st.selectbox(
        "Select Asset for Simulation", ["Bitcoin", "NVIDIA", "Gold"], key="mc_asset"
    )
    sim_days = st.slider("Simulation Horizon (Days)", 30, 252, 90)
    num_paths = st.slider("Number of Monte Carlo Paths", 50, 500, 100)
    run_mc = st.button("🎲 Run Monte Carlo Simulation", use_container_width=True)

  with col2:
    last_price = df_prices[mc_asset].iloc[-1]
    daily_rets = returns_df[mc_asset]
    mu = daily_rets.mean()
    sigma = daily_rets.std()

    # Simulate paths
    np.random.seed(42)
    dt = 1
    simulated_prices = np.zeros((sim_days, num_paths))
    simulated_prices[0] = last_price

    for t in range(1, sim_days):
      rand_normals = np.random.normal(0, 1, num_paths)
      simulated_prices[t] = simulated_prices[t - 1] * np.exp(
          (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rand_normals
      )

    fig_mc = go.Figure()
    for i in range(num_paths):
      fig_mc.add_trace(
          go.Scatter(
              y=simulated_prices[:, i],
              mode="lines",
              line=dict(width=1, color="rgba(59, 130, 246, 0.15)"),
              showlegend=False,
          )
      )

    # Add mean path
    mean_path = np.mean(simulated_prices, axis=1)
    fig_mc.add_trace(
        go.Scatter(
            y=mean_path,
            mode="lines",
            line=dict(width=3, color="#f59e0b"),
            name="Expected Path (Mean)",
        )
    )

    fig_mc.update_layout(
        title=f"Monte Carlo Forecast for {mc_asset} ({sim_days} Trading Days)",
        template="plotly_dark",
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Future Trading Days",
        yaxis_title="Simulated Price (₹/$)",
    )
    st.plotly_chart(fig_mc, use_container_width=True)

    p95 = np.percentile(simulated_prices[-1], 95)
    p05 = np.percentile(simulated_prices[-1], 5)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Spot Price", f"₹{last_price:,.2f}")
    c2.metric("Optimistic Target (95th %)", f"₹{p95:,.2f}")
    c3.metric("Downside Risk Bound (5th %)", f"₹{p05:,.2f}")

# --- TAB 2: PORTFOLIO OPTIMIZER ---
with tab_opt:
  st.subheader("Markowitz Mean-Variance Portfolio Optimizer")
  st.markdown(
      "Optimize capital allocation across Gold, Bitcoin, and NVIDIA to maximize"
      " the Sharpe Ratio."
  )

  col_opt_ctrl, col_opt_res = st.columns([1, 2], gap="large")

  with col_opt_ctrl:
    st.markdown("### Allocation Constraints")
    risk_free_rate = (
        st.slider("Assumed Risk-Free Rate (%)", 0.0, 10.0, 5.0, 0.5) / 100
    )
    opt_runs = st.number_input(
        "Optimization Iterations", value=2000, step=500
    )
    run_optimizer = st.button("⚡ Optimize Portfolio Weights", use_container_width=True)

  with col_opt_res:
    # Portfolio Optimization Simulation
    np.random.seed(42)
    num_assets = len(df_prices.columns)
    results = np.zeros((3 + num_assets, opt_runs))
    mean_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252

    for i in range(opt_runs):
      weights = np.random.random(num_assets)
      weights /= np.sum(weights)
      portfolio_return = np.sum(mean_returns * weights)
      portfolio_std_dev = np.sqrt(
          np.dot(weights.T, np.dot(cov_matrix, weights))
      )
      results[0, i] = portfolio_return
      results[1, i] = portfolio_std_dev
      results[2, i] = (
          portfolio_return - risk_free_rate
      ) / portfolio_std_dev  # Sharpe
      for j, w in enumerate(weights):
        results[3 + j, i] = w

    # Find max Sharpe portfolio
    max_sharpe_idx = np.argmax(results[2])
    optimal_weights = results[3:, max_sharpe_idx]

    st.markdown("### 🏆 Optimal Portfolio Allocation (Max Sharpe)")
    opt_df = pd.DataFrame(
        {
            "Asset": df_prices.columns,
            "Optimal Weight (%)": [f"{w*100:.2f}%" for w in optimal_weights],
        }
    )
    st.dataframe(opt_df, use_container_width=True, hide_index=True)

    # Display allocation pie chart
    fig_pie = px.pie(
        names=df_prices.columns,
        values=optimal_weights,
        title="Optimal Asset Allocation Distribution",
        template="plotly_dark",
    )
    fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 3: VALUE AT RISK (VaR) ---
with tab_var:
  st.subheader("Value at Risk (VaR) & Expected Shortfall (CVaR)")
  st.markdown(
      "Measure maximum expected portfolio loss over a 1-day holding period at"
      " 95% and 99% confidence intervals."
  )

  portfolio_daily_rets = returns_df.mean(axis=1)
  var_95 = np.percentile(portfolio_daily_rets, 5) * 100
  var_99 = np.percentile(portfolio_daily_rets, 1) * 100
  cvar_95 = (
      portfolio_daily_rets[portfolio_daily_rets <= np.percentile(portfolio_daily_rets, 5)].mean()
      * 100
  )

  v1, v2, v3 = st.columns(3)
  v1.metric("1-Day VaR (95% Confidence)", f"{var_95:.2f}%")
  v2.metric("1-Day VaR (99% Confidence)", f"{var_99:.2f}%")
  v3.metric("Expected Shortfall / CVaR (95%)", f"{cvar_95:.2f}%")

  fig_var = px.histogram(
      portfolio_daily_rets * 100,
      nbins=100,
      title="Portfolio Daily Return Distribution with VaR Cutoffs",
      template="plotly_dark",
  )
  fig_var.add_vline(
      x=var_95,
      line_dash="dash",
      line_color="orange",
      annotation_text="95% VaR Cutoff",
  )
  fig_var.add_vline(
      x=var_99,
      line_dash="dash",
      line_color="red",
      annotation_text="99% VaR Cutoff",
  )
  fig_var.update_layout(height=400)
  st.plotly_chart(fig_var, use_container_width=True)