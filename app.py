import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def get_stock_data(ticker, start_date, end_date):
    stock = yf.download(ticker, start=start_date, end=end_date)
    return stock

st.title("📈 Real-Time Stock Market Dashboard")  

# Sidebar for user inputs
st.sidebar.header("User Input")

# Stock Symbol Input
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, GOOGL)", "AAPL")

# Date Range Selection
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

start = st.sidebar.date_input("Start Date", datetime.strptime(start_date, "%Y-%m-%d"))
end = st.sidebar.date_input("End Date", datetime.strptime(end_date, "%Y-%m-%d"))

# Fetch Stock Data
if st.sidebar.button("Get Data"):
    stock_data = get_stock_data(ticker, start, end)
    st.write(f"### Stock Data for {ticker}")
    st.dataframe(stock_data.tail())  # Show last few rows

if 'stock_data' in locals():
    st.subheader("Stock Price Chart")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_data.index, stock_data['Close'], label="Closing Price", color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price")
    ax.set_title(f"{ticker} Stock Closing Price")
    ax.legend()
    st.pyplot(fig)

if 'stock_data' in locals():
    st.subheader("Moving Averages")

    # Calculate Moving Averages
    stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

    # Plot Moving Averages
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_data.index, stock_data['Close'], label="Closing Price", color='blue')
    ax.plot(stock_data.index, stock_data['MA20'], label="20-Day MA", color='red')
    ax.plot(stock_data.index, stock_data['MA50'], label="50-Day MA", color='green')

    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price")
    ax.set_title(f"{ticker} Stock Moving Averages")
    ax.legend()
    st.pyplot(fig)

if 'stock_data' in locals():
    st.subheader("Stock Volatility (Daily % Change)")

    stock_data['Daily Return'] = stock_data['Close'].pct_change() * 100

    # Plot Volatility
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_data.index, stock_data['Daily Return'], label="Daily % Change", color='purple')
    ax.set_xlabel("Date")
    ax.set_ylabel("Percentage Change")
    ax.set_title(f"{ticker} Daily Stock Volatility")
    ax.legend()
    st.pyplot(fig)

if 'stock_data' in locals():
    st.sidebar.subheader("Download Data")
    csv_data = stock_data.to_csv().encode('utf-8')
    st.sidebar.download_button("Download CSV", data=csv_data, file_name=f"{ticker}_data.csv", mime="text/csv")
