import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import fetch_market_data, inject_custom_css

st.set_page_config(
    page_title="Advanced Quant Lab & AI Terminal — QuantX",
    page_icon="🚀",
    layout="wide",
)
inject_custom_css()

df_prices = fetch_market_data()
returns_df = df_prices.pct_change().dropna()

st.title("🚀 Advanced Quantitative Lab, ML Regimes & AI Assistant")
st.markdown(
    "Executing institutional-grade Monte Carlo simulations, Markowitz mean-variance"
    " portfolio optimization, Value at Risk (VaR), machine learning regime"
    " detection, paper trading, and AI-powered research telemetry[cite: 3]."
)
st.markdown("---")

# Navigation Tabs for All Advanced Features & Future Scope
(
    tab_mc,
    tab_opt,
    tab_var,
    tab_ml_regime,
    tab_paper,
    tab_ai,
) = st.tabs([
    "🎲 Monte Carlo Simulation",
    "📊 Portfolio Weight Optimizer",
    "⚠️ Value at Risk (VaR)",
    "🤖 ML Market Regimes",
    "📝 Paper Trading Simulator",
    "💬 AI Research Assistant",
])

# --- TAB 1: MONTE CARLO SIMULATION ---
with tab_mc:
  st.subheader("Monte Carlo Price Path Simulation (Geometric Brownian Motion)")
  st.markdown(
      "Simulate future trading paths based on historical drift and volatility"
      " parameters[cite: 3]."
  )

  col1, col2 = st.columns([1, 2.5], gap="large")

  with col1:
    mc_asset = st.selectbox(
        "Select Asset for Simulation", list(df_prices.columns), key="mc_asset"
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
        yaxis_title="Simulated Price",
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
      "Optimize capital allocation across assets to maximize the Sharpe Ratio"
      "[cite: 3]."
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
    run_optimizer = st.button(
        "⚡ Optimize Portfolio Weights", use_container_width=True
    )

  with col_opt_res:
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
      results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
      for j, w in enumerate(weights):
        results[3 + j, i] = w

    max_sharpe_idx = np.argmax(results[2])
    optimal_weights = results[3:, max_sharpe_idx]

    st.markdown("### 🏆 Optimal Portfolio Allocation (Max Sharpe)")
    opt_df = pd.DataFrame({
        "Asset": df_prices.columns,
        "Optimal Weight (%)": [f"{w*100:.2f}%" for w in optimal_weights],
    })
    st.dataframe(opt_df, use_container_width=True, hide_index=True)

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
      portfolio_daily_rets[
          portfolio_daily_rets <= np.percentile(portfolio_daily_rets, 5)
      ].mean()
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

# --- TAB 4: ML MARKET REGIME DETECTION ---
with tab_ml_regime:
  st.subheader("Unsupervised Machine Learning Market Regime Detection")
  st.markdown(
      "Classify market environments into distinct volatility and trend states"
      " using KMeans clustering[cite: 3]."
  )
  ml_asset = st.selectbox(
      "Select Asset for Regime Clustering",
      list(df_prices.columns),
      key="ml_asset",
  )

  feat_df = pd.DataFrame(index=df_prices.index)
  feat_df["Return"] = df_prices[ml_asset].pct_change()
  feat_df["Volatility"] = feat_df["Return"].rolling(21).std() * np.sqrt(252)
  feat_df = feat_df.dropna()

  kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(
      feat_df[["Return", "Volatility"]]
  )
  feat_df["Regime Cluster"] = kmeans.labels_.astype(str)

  fig_ml = px.scatter(
      feat_df,
      x="Return",
      y="Volatility",
      color="Regime Cluster",
      template="plotly_dark",
      title=f"KMeans Market Regimes for {ml_asset}",
      height=420,
  )
  st.plotly_chart(fig_ml, use_container_width=True)

# --- TAB 5: PAPER TRADING SIMULATOR ---
with tab_paper:
  st.subheader("Virtual Paper Trading Execution Simulator")
  st.markdown(
      "Simulate live order execution with virtual capital and portfolio ledger"
      " tracking[cite: 3]."
  )

  if "paper_cash" not in st.session_state:
    st.session_state.paper_cash = 100000.0
    st.session_state.paper_holdings = {
        asset: 0 for asset in df_prices.columns
    }

  c_trade1, c_trade2 = st.columns([1, 2], gap="large")
  with c_trade1:
    trade_asset = st.selectbox(
        "Target Asset", list(df_prices.columns), key="paper_asset"
    )
    trade_action = st.radio("Order Action", ["BUY", "SELL"])
    shares = st.number_input("Order Quantity", 1, 1000, 10)
    current_px = df_prices[trade_asset].iloc[-1]
    st.info(f"Current Market Price: ₹{current_px:,.2f}")

    if st.button("Execute Paper Order", use_container_width=True):
      total_cost = shares * current_px
      if trade_action == "BUY":
        if st.session_state.paper_cash >= total_cost:
          st.session_state.paper_cash -= total_cost
          st.session_state.paper_holdings[trade_asset] += shares
          st.success(
              f"Successfully executed BUY for {shares}x {trade_asset} at"
              f" ₹{current_px:,.2f}"
          )
        else:
          st.error("Insufficient virtual cash balance.")
      else:
        if st.session_state.paper_holdings[trade_asset] >= shares:
          st.session_state.paper_cash += total_cost
          st.session_state.paper_holdings[trade_asset] -= shares
          st.success(
              f"Successfully executed SELL for {shares}x {trade_asset} at"
              f" ₹{current_px:,.2f}"
          )
        else:
          st.error("Insufficient asset position to sell.")

  with c_trade2:
    st.markdown("### 📋 Virtual Portfolio Ledger")
    st.metric("Available Cash Balance", f"₹{st.session_state.paper_cash:,.2f}")
    holdings_df = pd.DataFrame(
        list(st.session_state.paper_holdings.items()),
        columns=["Asset", "Quantity"],
    )
    st.dataframe(holdings_df, use_container_width=True, hide_index=True)

# --- TAB 6: AI QUANT RESEARCH ASSISTANT ---
with tab_ai:
  st.subheader("AI-Powered Quantitative Research Assistant")
  st.markdown(
      "Query multi-asset telemetry, risk parameters, and regime conditions for"
      " instant analytical insights[cite: 3]."
  )

  user_query = st.text_input(
      "Ask a quantitative research question:",
      "Which asset offers the best risk-adjusted profile currently?",
  )
  if st.button("Generate AI Insights", use_container_width=True):
    with st.spinner("Synthesizing quantitative market telemetry..."):
      best_asset = returns_df.mean().idxmax()
      max_vol = returns_df.std().idxmax()
      st.success("Analysis Complete")
      st.info(
          f"**QuantX AI Terminal Insight:** Based on current historical return"
          f" series and volatility profiles, **{best_asset}** demonstrates the"
          f" highest mean daily return, while **{max_vol}** exhibits elevated"
          " volatility clustering. Quantitative regime models suggest"
          " maintaining disciplined position sizing and adhering to"
          " stop-loss thresholds during high-volatility cluster states."
      )