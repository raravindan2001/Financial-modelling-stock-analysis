import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Institutional Equity Research", layout="wide")

def get_dcf_valuation(ticker, g_rate, d_rate):
    stock = yf.Ticker(ticker)
    # Fetching Free Cash Flow
    fcf = stock.cashflow.iloc[0, 0] if not stock.cashflow.empty else 0
    shares = stock.info.get('sharesOutstanding', 1)
    
    if fcf <= 0: return 0
    
    # Simple 5-year DCF Projection
    projections = [fcf * (1 + g_rate)**i for i in range(1, 6)]
    terminal_val = projections[-1] * (1 + 0.02) / (d_rate - 0.02)
    pv = sum([projections[i-1] / (1 + d_rate)**i for i in range(1, 6)]) + (terminal_val / (1 + d_rate)**5)
    
    return round(pv / shares, 2)

st.title("📊 Institutional Valuation Engine")

# Sidebar for Inputs
st.sidebar.header("Model Assumptions")
market = st.sidebar.selectbox("Market", ["US (NASDAQ/NYSE)", "India (NSE)"])
symbol = st.sidebar.text_input("Ticker Symbol", "AAPL" if market == "US (NASDAQ/NYSE)" else "RELIANCE.NS")
growth = st.sidebar.slider("Growth Rate (%)", 1, 30, 10) / 100
discount = st.sidebar.slider("Discount Rate (WACC %)", 5, 20, 9) / 100

if st.button("Run Financial Model"):
    data = yf.Ticker(symbol)
    curr_price = data.history(period="1d")['Close'].iloc[-1]
    intrinsic_val = get_dcf_valuation(symbol, growth, discount)
    
    # Main Display
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Market Price", f"{curr_price:.2f}")
    col2.metric("Model Intrinsic Value", f"{intrinsic_val}")
    
    upside = ((intrinsic_val - curr_price) / curr_price) * 100
    col3.metric("Projected Upside", f"{upside:.1f}%", delta_color="normal")

    # Sensitivity Analysis Table
    st.subheader("Sensitivity Analysis: Intrinsic Value vs. WACC & Growth")
    g_range = [growth - 0.02, growth - 0.01, growth, growth + 0.01, growth + 0.02]
    d_range = [discount + 0.02, discount + 0.01, discount, discount - 0.01, discount - 0.02]
    
    matrix = [[get_dcf_valuation(symbol, g, d) for g in g_range] for d in d_range]
    df_sens = pd.DataFrame(matrix, index=[f"WACC {int(d*100)}%" for d in d_range], 
                           columns=[f"Growth {int(g*100)}%" for g in g_range])
    st.table(df_sens)
