import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Institutional Equity Research", layout="wide")

def calculate_dcf(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # Financials for Modeling
    cash_flow = stock.cashflow
    if cash_flow.empty:
        return "Insufficient data for DCF"

    # Simplified Institutional Model Logic
    free_cash_flow = cash_flow.iloc[0, 0] # Most recent FCF
    growth_rate = 0.05  # Assume 5% conservative growth
    wacc = 0.09         # Assume 9% discount rate
    
    # Project 5 years
    projections = [free_cash_flow * (1 + growth_rate)**i for i in range(1, 6)]
    terminal_value = projections[-1] * 1.1 / (wacc - 0.02)
    pv_fcf = sum([projections[i-1] / (1 + wacc)**i for i in range(1, 6)])
    pv_tv = terminal_value / (1 + wacc)**5
    
    intrinsic_value = (pv_fcf + pv_tv) / info.get('sharesOutstanding', 1)
    return round(intrinsic_value, 2)

st.title("📊 Institutional Financial Modeling Platform")
st.sidebar.header("Market Selection")

market = st.sidebar.selectbox("Market", ["US (NYSE/NASDAQ)", "India (NSE)"])
ticker = st.sidebar.text_input("Enter Ticker (e.g., AAPL or RELIANCE.NS)", "AAPL")

if st.button("Run Institutional Model"):
    with st.spinner('Fetching Data from Exchanges...'):
        data = yf.Ticker(ticker)
        price = data.history(period="1d")['Close'].iloc[-1]
        valuation = calculate_dcf(ticker)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"{price:.2f}")
        col2.metric("Model Intrinsic Value", f"{valuation}")
        col3.metric("Margin of Safety", f"{((valuation - price)/valuation)*100:.1f}%")

        st.subheader("Historical Financials")
        st.dataframe(data.financials)
