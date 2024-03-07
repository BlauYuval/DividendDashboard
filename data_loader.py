import yfinance as yf
import pandas as pd
import streamlit as st

from utils import get_div_hist_per_stock

@st.cache
def get_daily_prices_data(tickers, start_time):
    """
    Get daily prices for a list of tickers from Yahoo Finance
    """
    daily_price = {}
    for t in tickers:
        ticker_price_history = yf.Ticker(t).history(period='1d', start=start_time, auto_adjust=False)
        ticker_price_history.index = pd.to_datetime(ticker_price_history.index).strftime('%Y-%m-%d')
        daily_price[t] = ticker_price_history.to_dict()['Close']
        
    return daily_price

@st.cache
def get_transacton_data(conn):
    """
    Get the transaction data
    """
    transaction_data = conn.read(spreadsheet=st.secrets['connections']['gsheets']['transactions'])
    transaction_data = transaction_data[['ticker', 'stock', 'activity_type', 'date', 'shares', 'stock_price',
        'amunt_paid', 'currency', 'commision_in_ils']].dropna().copy()

    return transaction_data

@st.cache
def get_dividend_data(transaction_data):
    """
    Get the dividend data
    """
    dividends_dict = {}
    tickers = transaction_data.ticker.unique()
    for ticker in tickers:
        dividends_dict[ticker] = get_div_hist_per_stock(ticker)
    
    return dividends_dict

@st.cache
def get_sector_data(conn):
    """
    Get the sector data
    """
    sectors_data = conn.read(spreadsheet=st.secrets['connections']['gsheets']['sectors'])
    sectors_data = sectors_data[['ticker', 'sector', 'industry']].dropna().copy()
    
    return sectors_data