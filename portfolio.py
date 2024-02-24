# In this script, we will create the portfolio data from the transaction data and sectors data.
# We will just present the stocks in the portfolio and the sectors they belong to.
# It will contain the following:
# - The stocks in the portfolio
# - The sectors they belong to
# - The total amount invested in each sector
# - The total amount invested in the portfolio

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

class Portfolio:
    
    def __init__(self, transaction_data, sectors_data):
        self.transaction_data = transaction_data
        self.sectors_data = sectors_data
        self.portfolio_data = None
        self.portfolio_by_sectors_data = None
        
    def get_current_holdings(self):
        """
        Get the current holdings from the transaction data
        """
        current_tickers = self.transaction_data.groupby('ticker').agg({'signed_shares':'sum'})
        current_tickers = current_tickers[current_tickers.signed_shares > 0].index.to_list()

        self.transaction_data['Amount Paid'] = self.transaction_data['signed_shares']*self.transaction_data['stock_price']
        
        self.portfolio_data = self.transaction_data.groupby('ticker').agg({'Amount Paid':'sum'})
        self.portfolio_data.reset_index(inplace=True)
        self.portfolio_data = self.portfolio_data[self.portfolio_data.ticker.isin(current_tickers)]

        
        
    def get_sectors(self):
        """
        Get the sectors from the sectors data
        """
        self.portfolio_data = self.portfolio_data.merge(self.sectors_data, how='left', on='ticker')
        
    def get_sector_investments(self):
        """
        Get the sector investments from the portfolio data
        """
        self.portfolio_by_sectors_data = self.portfolio_data.groupby('sector').agg({'Amount Paid':'sum'})
        self.portfolio_by_sectors_data.reset_index(inplace=True)
        
    def plot_pie_by_sectors(self):
        """
        Plot the bar chart by sectors
        """
        df_for_plot = self.portfolio_by_sectors_data.copy()
        df_for_plot['Amount Paid'] = df_for_plot['Amount Paid'].apply(lambda x: round(x, 2))
        df_for_plot['percent'] = (df_for_plot['Amount Paid']/df_for_plot['Amount Paid'].sum()).apply(lambda x: round(x, 2))*100
        colors = ['rgb(79, 129, 102)' for i in range(len(df_for_plot))]
        layout=go.Layout(width=400,height=400)
        fig = go.Figure(data=[go.Pie(labels=df_for_plot.sector,
                             values=df_for_plot.percent, insidetextorientation='radial')], layout=layout)
        fig.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=15,
                  marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))
        fig.update(layout_showlegend=False)
        fig.update_layout(margin=dict(t=10))
        
        col1, col2 = st.columns(2, gap='large')
        table_for_plot = self.portfolio_data.set_index('ticker').copy()
        table_for_plot['Amount Paid'] = table_for_plot['Amount Paid'].apply(lambda x: f'{int(x):,}$')
        table_for_plot = table_for_plot.rename(columns={'sector':'Sector', 'industry':'Industry'})
        
        col1.table(table_for_plot)
        col2.plotly_chart(fig)

    def plot_portoflio_tbl(self):
        """
        Process and plot the holding table
        """
        table_for_plot = self.portfolio_data.set_index('ticker').copy()
        table_for_plot['Amount Paid'] = table_for_plot['Amount Paid'].apply(lambda x: f'{int(x):,}$')
        table_for_plot = table_for_plot.rename(columns={'sector':'Sector', 'industry':'Industry'})
        
        st.table(table_for_plot)
        
    def plot_pie_by_sectors(self):
        """
        Plot the bar chart by sectors
        """
        df_for_plot = self.portfolio_by_sectors_data.copy()
        df_for_plot['Amount Paid'] = df_for_plot['Amount Paid'].apply(lambda x: round(x, 2))
        df_for_plot['percent'] = (df_for_plot['Amount Paid']/df_for_plot['Amount Paid'].sum()).apply(lambda x: round(x, 2))*100
        colors = ['rgb(79, 129, 102)' for i in range(len(df_for_plot))]
        layout=go.Layout(width=600,height=600)
        fig = go.Figure(data=[go.Pie(labels=df_for_plot.sector,
                             values=df_for_plot.percent, insidetextorientation='radial')], layout=layout)
        fig.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=15,
                  marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))
        fig.update(layout_showlegend=False)
        fig.update_layout(margin=dict(t=10))
        st.plotly_chart(fig)
        
        
    def run(self):
        """
        Run the portfolio
        """
        self.get_current_holdings()
        self.get_sectors()
        self.get_sector_investments()
        st.header("Portfolio")
        st.subheader("Current Holdings")
        self.plot_portoflio_tbl()
        st.subheader("Sectors")
        self.plot_pie_by_sectors()