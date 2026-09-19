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
    page_title="Strategy Lab — QuantX", page_icon="📈", layout="wide"
)
inject_custom_css()

df_prices = fetch_market_data()

st.title("⚡ Quantitative Strategy Lab & Backtest Execution")
st.markdown(
    "Configure quantitative rules, simulate friction costs, and audit trade"
    " execution timelines against buy-and-hold benchmarks."
)
st.markdown("---")

# Layout Configuration
col_config, col_results = st.columns([1, 2.2], gap="large")

with col_config:
  with st.container():
    st.markdown("### ⚙️ Backtest Parameters")
    strat_asset = st.selectbox(
        "Target Asset Universe", ["Bitcoin", "NVIDIA", "Gold"]
    )
    strategy_type = st.selectbox(
        "Quantitative Strategy Model",
        ["SMA Crossover", "EMA Trend", "Momentum", "Mean Reversion"],
    )

    st.markdown("#### Model Hyperparameters")
    short_window = st.slider("Fast / Short Window (Days)", 5, 50, 20)
    long_window = st.slider("Slow / Long Window (Days)", 30, 200, 50)

    st.markdown("#### Execution Constraints")
    initial_capital = st.number_input(
        "Initial Capital (₹)", value=100000, step=10000
    )
    tx_cost = (
        st.slider("Transaction Friction Cost (%)", 0.0, 0.5, 0.1, 0.05) / 100
    )

    run_sim = st.button("🚀 Run Backtest Simulation", use_container_width=True)

with col_results:
  prices = df_prices[strat_asset]

  # Strategy Signal Generation Logic
  if strategy_type == "SMA Crossover":
    fast_ma = prices.rolling(short_window).mean()
    slow_ma = prices.rolling(long_window).mean()
    signal = np.where(fast_ma > slow_ma, 1, 0)
  elif strategy_type == "EMA Trend":
    fast_ema = prices.ewm(span=short_window).mean()
    slow_ema = prices.ewm(span=long_window).mean()
    signal = np.where(fast_ema > slow_ema, 1, 0)
  elif strategy_type == "Momentum":
    mom = prices.pct_change(short_window)
    signal = np.where(mom > 0, 1, 0)
  else:
    ma = prices.rolling(short_window).mean()
    signal = np.where(prices < ma * 0.98, 1, 0)

  strat_ret = prices.pct_change().shift(-1) * signal
  strat_ret = strat_ret.fillna(0)
  trades = np.abs(np.diff(signal, prepend=0))
  strat_ret = strat_ret - (trades * tx_cost)

  portfolio_val = initial_capital * np.cumprod(1 + strat_ret)
  benchmark_val = initial_capital * (prices / prices.iloc[0])

  res_df = pd.DataFrame(
      {
          f"Strategy ({strategy_type})": portfolio_val,
          "Buy & Hold Benchmark": benchmark_val,
      },
      index=prices.index,
  )

  st.markdown("### 📊 Performance Equity Curve")
  fig_bt = px.line(res_df, template="plotly_dark")
  fig_bt.update_layout(
      height=380,
      margin=dict(l=10, r=10, t=10, b=10),
      hovermode="x unified",
      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
  )
  st.plotly_chart(fig_bt, use_container_width=True)

  # Key Metrics Display
  total_ret_strat = (
      (portfolio_val.iloc[-1] - initial_capital) / initial_capital
  ) * 100
  total_ret_bh = ((benchmark_val.iloc[-1] - initial_capital) / initial_capital) * 100
  trade_count = int(np.sum(trades))
  sharpe_strat = (strat_ret.mean() * 252) / (
      strat_ret.std() * np.sqrt(252) + 1e-8
  )

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Strategy Return", f"{total_ret_strat:.2f}%")
  m2.metric("Benchmark Return", f"{total_ret_bh:.2f}%")
  m3.metric("Sharpe Ratio", f"{sharpe_strat:.2f}")
  m4.metric("Total Trades Executed", f"{trade_count}")

  # Interactive Trade Timeline Log
  st.markdown("### 📋 Trade Execution Log")
  trade_indices = np.where(trades > 0)[0]
  trade_log_data = []
  for idx in trade_indices[-10:]:  # Show last 10 trades
    action = "BUY (Long)" if signal[idx] == 1 else "SELL (Exit)"
    trade_log_data.append(
        {
            "Date": prices.index[idx].strftime("%Y-%m-%d"),
            "Action": action,
            "Execution Price (₹)": f"{prices.iloc[idx]:,.2f}",
            "Portfolio Valuation": f"₹{portfolio_val.iloc[idx]:,.2f}",
        }
    )

  if trade_log_data:
    st.dataframe(
        pd.DataFrame(trade_log_data), use_container_width=True, hide_index=True
    )
  else:
    st.info(
        "No trade executions recorded with current parameter configurations."
    )