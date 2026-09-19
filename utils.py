import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300)
def fetch_market_data():
  tickers = {"Gold": "GC=F", "Bitcoin": "BTC-USD", "NVIDIA": "NVDA"}
  try:
    df = yf.download(
        list(tickers.values()), start="2020-01-01", progress=False
    )["Close"]
    if isinstance(df, pd.DataFrame):
      if hasattr(df.columns, "droplevel"):
        try:
          df.columns = df.columns.droplevel(0)
        except Exception:
          pass
      inv_tickers = {v: k for k, v in tickers.items()}
      df = df.rename(columns=inv_tickers)
      for name in ["Gold", "Bitcoin", "NVIDIA"]:
        if name not in df.columns:
          df[name] = 100.0
      df = df[["Gold", "Bitcoin", "NVIDIA"]].ffill().dropna()
      if not df.empty:
        return df
  except Exception:
    pass

  # Offline/Rate-limit Robust Fallback Simulation
  np.random.seed(42)
  dates = pd.date_range(start="2020-01-01", end="2026-09-01", freq="B")
  n = len(dates)
  gold_ret = np.random.normal(0.0003, 0.009, n)
  btc_ret = np.random.normal(0.0012, 0.035, n)
  nvda_ret = np.random.normal(0.0015, 0.028, n)
  df = pd.DataFrame(
      {
          "Gold": 45000 * np.cumprod(1 + gold_ret),
          "Bitcoin": 3000000 * np.cumprod(1 + btc_ret),
          "NVIDIA": 4000 * np.cumprod(1 + nvda_ret),
      },
      index=dates,
  )
  return df


def inject_custom_css():
  st.markdown(
      """
    <style>
    /* Global Terminal Theme & Deep Space Background */
    .main { 
        background: radial-gradient(circle at top right, #0f172a 0%, #07090e 60%); 
        color: #f3f4f6; 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
    }
    .stSidebar { 
        background-color: #0b0f19; 
        border-right: 1px solid rgba(255, 255, 255, 0.08); 
    }
    
    /* Futuristic Glow Buttons */
    div.stButton > button { 
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
        color: white; 
        border-radius: 10px; 
        font-weight: 600; 
        border: 1px solid rgba(59, 130, 246, 0.4); 
        padding: 0.6rem 1.4rem; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);
    }
    div.stButton > button:hover { 
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); 
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.45);
        transform: translateY(-2px);
        border-color: #60a5fa;
    }

    /* Glassmorphism FinTech Cards */
    .glass-card {
        background: rgba(22, 27, 34, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }

    /* Typography & Headers */
    h1, h2, h3 { 
        color: #f8fafc; 
        font-weight: 800; 
        letter-spacing: -0.03em; 
    }
    p, span, label, .stMarkdown { 
        color: #94a3b8; 
    }
    
    /* Live Telemetry Badge */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        gap: 6px;
    }
    .pulsing-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px #34d399; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    </style>
    """,
      unsafe_allow_html=True,
  )