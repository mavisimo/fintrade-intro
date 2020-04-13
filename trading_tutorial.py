#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:48:26 2020

@author: maviszeng

Running through practice and examples of using python for financial trading
from DataCamp.
"""
#%%

# Importing financial data
import pandas as pd
import pandas_datareader as pdr
import datetime

aapl = pdr.get_data_yahoo('AAPL',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))

# Save data to csv file
# aapl.to_csv('data/aapl_ohlc.csv')
# df = pd.read_csv('data/aapl_ohlc.csv', header=0, index_col='Date', 
#                 parse_dates=True)

#%%

# Displays
aapl.head()
aapl.tail()
aapl.describe()

aapl.index
aapl.columns
ts = aapl['Close'][-10:]
type(ts)

# Indexing
# first rows of November-December 2006
print(aapl.loc[pd.Timestamp('2006-11-01'):pd.Timestamp('2006-12-31')].head())
# first rows of 2007 
print(aapl.loc['2007'].head())
# November 2006
print(aapl.iloc[22:43])
# Open and Close values at 2006-11-01 and 2006-12-01
print(aapl.iloc[[22,43], [0, 3]])

# Sampling
sample = aapl.sample(20)
print(sample)
monthly_aapl = aapl.resample('M').mean()
print(monthly_aapl)
#aapl.asfreq("M", method="bfill")


#%%

# Calculating daily difference of opening and closing prices
aapl['diff'] = aapl.Open - aapl.Close

#%%
import matplotlib.pyplot as plt

# Visualization of time series
aapl['diff'].plot(grid=True)
plt.show()

aapl['Close'].plot(grid=True)
plt.show()









