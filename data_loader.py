import yfinance as yf
import pandas as pd

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