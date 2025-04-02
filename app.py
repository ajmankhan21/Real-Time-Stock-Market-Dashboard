import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from yahoo_fin import stock_info

# Alpha Vantage API Key (replace with your own)
API_KEY = "MJS5WX9E2P6WF5UZ"  # Get your API key from https://www.alphavantage.co/support/#api-key

# Function to get stock symbol based on company name with multiple suggestions
def get_stock_symbol_suggestions(company_name):
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    suggestions = []
    if "bestMatches" in data and len(data["bestMatches"]) > 0:
        for match in data["bestMatches"]:
            suggestions.append({
                "symbol": match["1. symbol"],
                "name": match["2. name"]
            })
    return suggestions

# Function to fetch stock data from Alpha Vantage
@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        stock_data = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        stock_data = stock_data.rename(columns={
            "1. open": "Open", "2. high": "High", "3. low": "Low", "4. close": "Close", "5. volume": "Volume"
        })
        stock_data.index = pd.to_datetime(stock_data.index)
        stock_data = stock_data.sort_index()
        stock_data = stock_data[(stock_data.index >= pd.to_datetime(start_date)) & (stock_data.index <= pd.to_datetime(end_date))]
        return stock_data
    return None

# Function to fetch stock news from Alpha Vantage (with error handling)
@st.cache_data
def get_stock_news_alpha_vantage(ticker):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&symbol={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    news = []
    if "feed" in data:
        for article in data["feed"]:
            news.append({
                "title": article.get("title", "No title available"),
                "link": article.get("url", ""),
                "published_at": article.get("published_at", "Unknown date"),  # Handle missing date
                "summary": article.get("summary", "No summary available"),
                "image_url": article.get("image_url", None)  # Handle missing image URL
            })
    return news

# Function to fetch stock news from Yahoo Finance (with images)
@st.cache_data
def get_stock_news_yahoo(ticker):
    news = stock_info.get_news(ticker)
    
    news_articles = []
    for article in news:
        news_articles.append({
            "title": article["title"],
            "link": article["link"],
            "published_at": article.get("date", "Unknown date"),  # Handle missing date
            "summary": article["summary"],
            "image_url": article.get("image", None)
        })
    return news_articles

# Streamlit UI
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar for user input
st.sidebar.header("Search for a Stock")

company_name = st.sidebar.text_input("Enter Company Name (e.g., Apple, Tesla)", "Apple")
suggestions = get_stock_symbol_suggestions(company_name)

if suggestions:
    # Dropdown with multiple suggestions
    symbol_choices = [f"{suggestion['name']} ({suggestion['symbol']})" for suggestion in suggestions]
    selected_symbol = st.sidebar.selectbox("Select a Stock", symbol_choices)
    
    # Extract the symbol from the selected suggestion
    stock_symbol = [suggestion['symbol'] for suggestion in suggestions if f"{suggestion['name']} ({suggestion['symbol']})" == selected_symbol][0]
    st.sidebar.success(f"Selected Symbol: {stock_symbol}")
else:
    st.sidebar.error("No suggestions found.")

start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.today())

if st.sidebar.button("Search"):
    if stock_symbol:
        # Fetch stock data using the symbol
        stock_data = get_stock_data(stock_symbol, start_date, end_date)
        
        if stock_data is not None:
            # Convert 'Close' column to numeric (float) to avoid errors
            stock_data['Close'] = pd.to_numeric(stock_data['Close'], errors='coerce')
            
            # Calculate daily return (percentage change)
            stock_data['Daily Return'] = stock_data['Close'].pct_change() * 100

            st.write(f"### Stock Data for {company_name} ({stock_symbol})")
            st.dataframe(stock_data.tail())  # Show last few rows
            
            # Plot Stock Price
            st.subheader("Stock Price Chart")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(stock_data.index, stock_data['Close'], label="Closing Price", color='blue')
            ax.set_xlabel("Date")
            ax.set_ylabel("Stock Price")
            ax.set_title(f"{company_name} Stock Closing Price")
            ax.legend()
            st.pyplot(fig)

            # Moving Averages
            st.subheader("Moving Averages")
            stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(stock_data.index, stock_data['Close'], label="Closing Price", color='blue')
            ax.plot(stock_data.index, stock_data['MA20'], label="20-Day MA", color='red')
            ax.plot(stock_data.index, stock_data['MA50'], label="50-Day MA", color='green')
            ax.set_xlabel("Date")
            ax.set_ylabel("Stock Price")
            ax.set_title(f"{company_name} Stock Moving Averages")
            ax.legend()
            st.pyplot(fig)

            # Volatility (Daily % Change)
            st.subheader("Stock Volatility (Daily % Change)")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(stock_data.index, stock_data['Daily Return'], label="Daily % Change", color='purple')
            ax.set_xlabel("Date")
            ax.set_ylabel("Percentage Change")
            ax.set_title(f"{company_name} Daily Stock Volatility")
            ax.legend()
            st.pyplot(fig)

            # Fetch and display news from Alpha Vantage
            st.subheader(f"Latest News for {company_name} ({stock_symbol}) from Alpha Vantage")
            alpha_vantage_news = get_stock_news_alpha_vantage(stock_symbol)
            
            if alpha_vantage_news:
                for article in alpha_vantage_news:
                    st.write(f"### [{article['title']}]({article['link']})")
                    st.write(f"**Published At:** {article['published_at']}")
                    st.write(f"**Summary:** {article['summary']}")
                    if article["image_url"]:
                        st.image(article["image_url"], width=150)
                    st.write("---")
            else:
                st.write("No news available from Alpha Vantage.")
            
            # Download option for CSV file
            st.sidebar.subheader("Download Data")
            csv_data = stock_data.to_csv().encode('utf-8')
            st.sidebar.download_button("Download CSV", data=csv_data, file_name=f"{company_name}_data.csv", mime="text/csv")
        
        else:
            st.error("Failed to retrieve stock data. Please try again later.")
    else:
        st.sidebar.error("Company not found. Try another name.")
