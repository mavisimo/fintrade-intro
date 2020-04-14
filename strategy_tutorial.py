#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 15:28:28 2020

@author: maviszeng

Implementing trading strategies as outlined in DataCamp tutorial of trading.
"""

#%%
import pandas as pd
import pandas_datareader as pdr
import datetime
import numpy as np
import matplotlib.pyplot as plt

aapl = pdr.get_data_yahoo('AAPL',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))


#%%

""" Moving Average Crossover """

short_window = 30
long_window = 120
signals = pd.DataFrame(index=aapl.index)
signals['signal'] = 0.0

signals['shortm_avg'] = aapl['Close'].rolling(window=short_window,
       min_periods=1,center=False).mean()
signals['longm_avg'] = aapl['Close'].rolling(window=long_window,
       min_periods=1,center=False).mean()
signals['signal'][short_window:] = np.where(signals['shortm_avg'][short_window:]
        > signals['longm_avg'][short_window:],1.0,0.0)
signals['long_short'] = signals['signal'].diff()

print(signals)


fig = plt.figure()
ax1 = fig.add_subplot(111,  ylabel='Price in $')

aapl['Close'].plot(ax=ax1, color='r', lw=1)
signals[['shortm_avg', 'longm_avg']].plot(ax=ax1, lw=1)
ax1.plot(signals.loc[signals.long_short == 1.0].index, signals.shortm_avg
         [signals.long_short == 1.0],'^', markersize=8, color='m')
ax1.plot(signals.loc[signals.long_short == -1.0].index, signals.shortm_avg
         [signals.long_short == -1.0],'v', markersize=8, color='k')

plt.show()

""" Backtesting """

initial_capital = 6000
positions = pd.DataFrame(index=signals.index)
positions['AAPL'] = 100*signals['signal']
portfolio = positions.multiply(aapl['Adj Close'],axis=0)
pos_diff = positions.diff() # new DataFrame

portfolio['holdings'] = (positions.multiply(aapl['Adj Close'],
         axis=0)).sum(axis=1)
portfolio['cash'] = initial_capital - (pos_diff.multiply(aapl['Adj Close'], 
         axis=0)).sum(axis=1).cumsum()
portfolio['total'] = portfolio['holdings'] + portfolio['cash']
portfolio['returns'] = portfolio['total'].pct_change()

print(portfolio.head())


fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')

portfolio['total'].plot(ax=ax1, lw=1)
ax1.plot(portfolio.loc[signals.long_short == 1.0].index, portfolio.total
         [signals.long_short == 1.0], '^', markersize=8, color='m')
ax1.plot(portfolio.loc[signals.positions == -1.0].index, portfolio.total
         [signals.positions == -1.0], 'v', markersize=8, color='k')

plt.show()



