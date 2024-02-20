import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

from utils import get_div_hist_per_stock
from data_preprocessor import TransactionDataPreprocessing
from income import Income
from growth import DividendGrowth
from portfolio import Portfolio
from data_preprocessor import TransactionDataPreprocessing, DividendDataPreprocessor

# st.set_page_config(layout="wide")

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
# dividends_data.to_csv("data/dividend_data_preprocessed.csv", index=False)

sectors_data = conn.read(spreadsheet=st.secrets['connections']['gsheets']['sectors'])
sectors_data = sectors_data[['ticker', 'sector', 'industry']].dropna().copy()
# sectors_data = pd.read_csv("data/sectors.csv")

st.title("Portfolio")

portfolio = Portfolio(transaction_data, sectors_data)
portfolio.run()

st.title("Income")
    
income = Income(transaction_data, dividends_data)
income.get_income_data()
income.get_income_streamlit_bullet()
income.get_income_bar_chart()

st.title("Growth")

tickers = portfolio.portfolio_data.ticker.to_list()
growth = DividendGrowth(income.transaction_data[['ticker','start_payment_date']], dividends_data, tickers)
growth_df = growth.merge_prev_and_forward_growth()
st.dataframe(growth.plot(growth_df))