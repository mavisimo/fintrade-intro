#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:48:26 2020

@author: maviszeng

Running through practice and examples of using python for financial trading
from DataCamp.
"""
#%%

""" Importing financial data """
import pandas as pd
import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt
import numpy as np

aapl = pdr.get_data_yahoo('AAPL',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
# Save data to csv file
# aapl.to_csv('data/aapl_ohlc.csv')
# df = pd.read_csv('data/aapl_ohlc.csv', header=0, index_col='Date', 
#                 parse_dates=True)

def get(tickers, startdate, enddate):
  def data(ticker):
    return (pdr.get_data_yahoo(ticker, start=startdate, end=enddate))
  datas = map(data, tickers)
  return(pd.concat(datas, keys=tickers, names=['Ticker', 'Date']))
tickers = ['AAPL', 'MSFT', 'IBM', 'GOOG']
all_data = get(tickers, datetime.datetime(2014, 10, 1), 
               datetime.datetime(2020, 1, 1))


#%%

""" Displays """
aapl.head()
aapl.tail()
aapl.describe()

aapl.index
aapl.columns
ts = aapl['Close'][-10:]
type(ts)

""" Indexing """
# first rows of November-December 2006
print(aapl.loc[pd.Timestamp('2006-11-01'):pd.Timestamp('2006-12-31')].head())
# first rows of 2007 
print(aapl.loc['2007'].head())
# November 2006
print(aapl.iloc[22:43])
# Open and Close values at 2006-11-01 and 2006-12-01
print(aapl.iloc[[22,43], [0, 3]])

""" Sampling """
sample = aapl.sample(20)
print(sample)
monthly_aapl = aapl.resample('M').mean()
print(monthly_aapl)
#aapl.asfreq("M", method="bfill")


#%%

# Calculating daily difference of opening and closing prices
aapl['diff'] = aapl.Open - aapl.Close

""" Visualization of time series """

aapl['diff'].plot(grid=True)
plt.show()
aapl['Close'].plot(grid=True)
plt.show()


#%%

""" Financial Analysis: Returns """

# Daily Returns
daily_close = aapl[['Adj Close']]
daily_pct_change = daily_close.pct_change()
daily_pct_change.fillna(0, inplace=True)
#daily_pct_change = daily_close / daily_close.shift(1) - 1
daily_pct_change.hist(bins=50)
plt.show()
print(daily_pct_change.describe())

cum_daily_return = (1 + daily_pct_change).cumprod()
cum_daily_return.plot(figsize=(12,8))
plt.show()

daily_log_returns = np.log(daily_close.pct_change()+1)
#daily_log_returns_shift = np.log(daily_close / daily_close.shift(1)))


# Monthly Returns
monthly = aapl.resample('BM').apply(lambda x: x[-1])
monthly.pct_change()
cum_monthly_return = cum_daily_return.resample("M").mean()

# Quarterly Returns
quarter = aapl.resample("4M").mean()
quarter.pct_change()


""" Returns Multiple Comparison Charts """

daily_close_px = all_data[['Adj Close']].reset_index().pivot('Date', 
                         'Ticker', 'Adj Close')
daily_pct_change = daily_close_px.pct_change()
daily_pct_change.hist(bins=50, sharex=True, figsize=(12,8))
plt.show()
pd.plotting.scatter_matrix(daily_pct_change, diagonal='kde', 
                           alpha=0.1,figsize=(12,12))
plt.show()


#%%

""" Moving Windows """

adj_close_px = aapl['Adj Close']
moving_avg = adj_close_px.rolling(window=40).mean()
print(moving_avg[-10:])

aapl['42'] = adj_close_px.rolling(window=40).mean()
aapl['252'] = adj_close_px.rolling(window=252).mean()
aapl[['Adj Close', '42', '252']].plot()
plt.show()

# Volatility
min_periods = 75 
vol = daily_pct_change.rolling(min_periods).std() * np.sqrt(min_periods) 
vol.plot(figsize=(10, 8))
plt.show()

#%%

""" Regression Analysis """

import statsmodels.api as sm

all_adj_close = all_data[['Adj Close']]
all_returns = np.log(all_adj_close / all_adj_close.shift(1))

aapl_returns = all_returns.iloc[all_returns.index.get_level_values('Ticker') == 'AAPL']
aapl_returns.index = aapl_returns.index.droplevel('Ticker')

msft_returns = all_returns.iloc[all_returns.index.get_level_values('Ticker') == 'MSFT']
msft_returns.index = msft_returns.index.droplevel('Ticker')

return_data = pd.concat([aapl_returns, msft_returns], axis=1)[1:]
return_data.columns = ['AAPL', 'MSFT']
X = sm.add_constant(return_data['AAPL'])
model = sm.OLS(return_data['MSFT'],X).fit()
print(model.summary())

plt.plot(return_data['AAPL'], return_data['MSFT'], 'r.')
ax = plt.axis()
x = np.linspace(ax[0], ax[1] + 0.01)
plt.plot(x, model.params[0] + model.params[1] * x, 'b', lw=2)

plt.grid(True)
plt.axis('tight')
plt.xlabel('Apple Returns')
plt.ylabel('Microsoft returns')
plt.show()

#rolling correlation
return_data['MSFT'].rolling(window=252).corr(return_data['AAPL']).plot()
plt.show()


