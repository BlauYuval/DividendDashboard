import streamlit as st
from streamlit_gsheets import GSheetsConnection

from utils import get_div_hist_per_stock
from data_loader import get_daily_prices_data, get_transacton_data, get_dividend_data, get_sector_data
from data_preprocessor import TransactionDataPreprocessing
from income import Income
from growth import DividendGrowth
from portfolio import Portfolio
from portfolio_returns import PortfolioReturns
from executive_summery import ExecutiveSummery
from data_preprocessor import TransactionDataPreprocessing, DividendDataPreprocessor
from login import login

authentication_status, name = login()
# authentication_status, name = True, 'User1'
if authentication_status:

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    transaction_data = get_transacton_data(conn)
    transaction_preprocessor = TransactionDataPreprocessing(transaction_data)
    transaction_preprocessor.run()
    transaction_data = transaction_preprocessor.df.copy()

    dividends_dict = get_dividend_data(transaction_data)
    dividend_preprocessor = DividendDataPreprocessor()
    dividend_preprocessor.preprocess_multiple_tickers_data(dividends_dict)
    dividends_data = dividend_preprocessor.df.copy()

    sectors_data = get_sector_data(conn)

    daily_prices = get_daily_prices_data(transaction_data.ticker.unique(), transaction_data.date.min())

    st.markdown(f"<h1 style='text-align: center; color: white;'>{name} - Dividend Dashboard", unsafe_allow_html=True)
    #Engine
    ## PORTFOLIO
    portfolio = Portfolio(transaction_data, sectors_data)
    portfolio.run()  
    portfolio_returns = PortfolioReturns(transaction_data.rename(columns={'signed_shares':'shares'}), daily_prices)
    total_amounts = portfolio_returns.run()
    ## INCOME
    income = Income(transaction_data, dividends_data)
    monthly_income, yearly_income = income.run()
    
    ## GROWTH
    tickers = portfolio.portfolio_data.ticker.to_list()
    growth = DividendGrowth(income.transaction_data[['ticker','start_payment_date']], dividends_data, tickers)
    growth_df = growth.run()
    
    #Display
    ## Excetive Summary
    summery = ExecutiveSummery(portfolio, portfolio_returns, income, growth)
    total_return, amount_invested, return_yield = summery.get_total_return()
    dividend_yield, yield_on_cost = summery.get_dividend_yield(total_return, amount_invested, yearly_income)
    average_dividend_growth = summery.get_average_dividend_growth(growth_df)
    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Return", f"{int(total_return):,}$")
    col2.metric("Return Yield", f"{round(return_yield, 2)}%")
    col3.metric("Yield on Cost", f"{round(yield_on_cost, 2)}%")
    col4.metric("Average Dividend Growth", f"{round(average_dividend_growth, 2)}%")
    # new line of space
    st.write("")
    st.write("")
    
    ## PORTFOLIO
    st.header("Portfolio") 
    st.subheader("Current Holdings")
    portfolio.plot_portoflio_tbl()
    st.subheader("Sectors")
    portfolio.plot_pie_by_sectors()
    st.subheader("Portfolio Returns")
    portfolio_returns.plot_portfolio(total_amounts, transaction_data['date'].min(), portfolio_returns.today)

    ## INCOME
    st.header("Income")
    income.get_income_streamlit_bullet(monthly_income, yearly_income)
    income.get_income_bar_chart()

    ## GROWTH
    st.header("Dividend Growth")
    st.table(growth.plot(growth_df))