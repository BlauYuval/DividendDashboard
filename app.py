import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

from utils import get_div_hist_per_stock
from data_loader import get_daily_prices_data
from data_preprocessor import TransactionDataPreprocessing
from income import Income
from growth import DividendGrowth
from portfolio import Portfolio
from portfolio_returns import PortfolioReturns
from data_preprocessor import TransactionDataPreprocessing, DividendDataPreprocessor
from login import login

# authentication_status, name = login()
authentication_status, name = True, 'Yuval Blau'
if authentication_status:

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    transaction_data = conn.read(spreadsheet=st.secrets['connections']['gsheets']['transactions'])
    transaction_data = transaction_data[['ticker', 'stock', 'activity_type', 'date', 'shares', 'stock_price',
        'amunt_paid', 'currency', 'commision_in_ils']].dropna().copy()

    transaction_preprocessor = TransactionDataPreprocessing(transaction_data)
    transaction_preprocessor.run()
    transaction_data = transaction_preprocessor.df.copy()

    dividends_dict = {}
    tickers = transaction_data.ticker.unique()
    for ticker in tickers:
        dividends_dict[ticker] = get_div_hist_per_stock(ticker)
    dividend_preprocessor = DividendDataPreprocessor()
    dividend_preprocessor.preprocess_multiple_tickers_data(dividends_dict)
    dividends_data = dividend_preprocessor.df.copy()

    sectors_data = conn.read(spreadsheet=st.secrets['connections']['gsheets']['sectors'])
    sectors_data = sectors_data[['ticker', 'sector', 'industry']].dropna().copy()

    daily_prices = get_daily_prices_data(transaction_data.ticker.unique(), transaction_data.date.min())

    st.markdown(f"<h1 style='text-align: center; color: white;'>{name} - Dividend Dashboard", unsafe_allow_html=True)
    # PORTFOLIO

    portfolio = Portfolio(transaction_data, sectors_data)
    portfolio.run()
    ticker = st.text_input('Valid Uppercase Ticker:', 'SCHD')
    portfolio_returns = PortfolioReturns(transaction_data.rename(columns={'signed_shares':'shares'}), daily_prices)
    portfolio_returns.run(transaction_data['date'].min(), portfolio_returns.today, ticker)

    # INCOME
        
    income = Income(transaction_data, dividends_data)
    income.run()

    # GROWTH

    tickers = portfolio.portfolio_data.ticker.to_list()
    growth = DividendGrowth(income.transaction_data[['ticker','start_payment_date']], dividends_data, tickers)
    growth.run()