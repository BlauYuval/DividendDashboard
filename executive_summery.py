# In this script wew will create executive summery for the entire app.
# This should include streamlit metrics, including this info: Total Return, Dividend Yield, Yield on Cost, Average Dividend Growth, Income.
import streamlit as st

class ExecutiveSummery:
    
    def __init__(self, portfolio, portfolio_returns, income, growth):
        self.portfolio = portfolio
        self.portfolio_returns = portfolio_returns
        self.income = income
        self.growth = growth
        
    def get_total_return(self):
        """
        Get the total return
        """
        total_return = self.portfolio.portfolio_data['Current Amount'].sum()
        amount_invested = self.portfolio.portfolio_data['Amount Paid'].sum()
        return_yield = 100*((total_return - amount_invested) / amount_invested)
        return total_return, amount_invested, return_yield
    
    def get_dividend_yield(self, total_return, amount_invested, yearly_income):
        """
        Get the dividend yield
        """
        dividend_yield = 100*(yearly_income / total_return)
        yield_on_cost = 100*(yearly_income / amount_invested)
        return dividend_yield, yield_on_cost
        
    def get_average_dividend_growth(self, growth_df):
        """
        Get the average dividend growth
        """
        portfolio_data = self.portfolio.portfolio_data.groupby('ticker').agg({'Amount Paid':'sum'})
        df = growth_df.set_index('ticker').merge(portfolio_data, left_index=True, right_index=True)
        df = df.dropna(subset=['CAGR Since Holding'])
        average_dividend_growth = (df['CAGR Since Holding']*df['Amount Paid']).sum()/df['Amount Paid'].sum()
        
        return average_dividend_growth
        