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
import statsmodels.api as sm

def initialize(ticker):
    data = pdr.get_data_yahoo(ticker,start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
    return data

aapl = pdr.get_data_yahoo('AAPL',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
aapl.to_csv('aapl_data.csv')
writer = pd.ExcelWriter('aapl_data.xlsx', engine='xlsxwriter')
aapl.to_excel(writer, sheet_name='Yahoo Data')

benchmark = pdr.get_data_yahoo('SPY',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))


#%%

""" Moving Average Crossover """

def strategy(data,short_window,long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0
    signals['shortm_avg'] = data['Close'].rolling(window=short_window,
           min_periods=1,center=False).mean()
    signals['longm_avg'] = data['Close'].rolling(window=long_window,
           min_periods=1,center=False).mean()
    signals['signal'][short_window:] = np.where(signals['shortm_avg']
        [short_window:] > signals['longm_avg'][short_window:],1.0,0.0)
    signals['long_short'] = signals['signal'].diff()
    return signals
    
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
signals.to_excel(writer, sheet_name='Strategy')

fig = plt.figure()
ax1 = fig.add_subplot(111,  ylabel='Price in $')

aapl['Close'].plot(ax=ax1, color='r', lw=1)
signals[['shortm_avg', 'longm_avg']].plot(ax=ax1, lw=1)
ax1.plot(signals.loc[signals.long_short == 1.0].index, signals.shortm_avg
         [signals.long_short == 1.0],'^', markersize=8, color='m')
ax1.plot(signals.loc[signals.long_short == -1.0].index, signals.shortm_avg
         [signals.long_short == -1.0],'v', markersize=8, color='k')

plt.show()

#%%

""" Backtesting """

def portfolios(ticker, data, signals, shares, initial_capital):
    positions = pd.DataFrame(index=signals.index)
    positions[ticker] = shares*signals['signal']
    portfolio = positions.multiply(data['Adj Close'],axis=0)
    pos_diff = positions.diff() # new DataFrame
    portfolio['holdings'] = (positions.multiply(data['Adj Close'],
         axis=0)).sum(axis=1)
    portfolio['cash'] = initial_capital - (pos_diff.multiply(data['Adj Close'], 
         axis=0)).sum(axis=1).cumsum()
    portfolio['total'] = portfolio['holdings'] + portfolio['cash']
    portfolio['returns'] = portfolio['total'].pct_change()
    return portfolio

initial_capital = 6000
positions = pd.DataFrame(index=signals.index)
positions['AAPL'] = 100*signals['signal']
portfolio = positions.multiply(aapl['Adj Close'],axis=0)
pos_diff = positions.diff()

portfolio['holdings'] = (positions.multiply(aapl['Adj Close'],
         axis=0)).sum(axis=1)
portfolio['cash'] = initial_capital - (pos_diff.multiply(aapl['Adj Close'], 
         axis=0)).sum(axis=1).cumsum()
portfolio['total'] = portfolio['holdings'] + portfolio['cash']
portfolio['returns'] = portfolio['total'].pct_change()

print(portfolio.head())
portfolio.to_excel(writer, sheet_name='Portfolio')

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
portfolio['total'].plot(ax=ax1, lw=1)
ax1.plot(portfolio.loc[signals.long_short == 1.0].index, portfolio.total
         [signals.long_short == 1.0], '^', markersize=8, color='m')
ax1.plot(portfolio.loc[signals.long_short == -1.0].index, portfolio.total
         [signals.long_short == -1.0], 'v', markersize=8, color='k')

plt.show()

writer.save()

#%%

def backtest(data, signals, portfolio):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111,  ylabel='Price in $')
    data['Close'].plot(ax=ax1, color='r', lw=1)
    signals[['shortm_avg', 'longm_avg']].plot(ax=ax1, lw=1)
    ax1.plot(signals.loc[signals.long_short == 1.0].index, signals.shortm_avg
         [signals.long_short == 1.0],'^', markersize=8, color='m')
    ax1.plot(signals.loc[signals.long_short == -1.0].index, signals.shortm_avg
         [signals.long_short == -1.0],'v', markersize=8, color='k')
    plt.show()
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, ylabel='Portfolio value in $')
    portfolio['total'].plot(ax=ax2, lw=1)
    ax2.plot(portfolio.loc[signals.long_short == 1.0].index, portfolio.total
         [signals.long_short == 1.0], '^', markersize=8, color='m')
    ax2.plot(portfolio.loc[signals.long_short == -1.0].index, portfolio.total
         [signals.long_short == -1.0], 'v', markersize=8, color='k')
    plt.show()

def save(ticker, data, signals, portfolio):
    file_name = ticker + '_data.xlsx'
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Yahoo Data')
    signals.to_excel(writer, sheet_name='Strategy')
    portfolio.to_excel(writer, sheet_name='Portfolio')
    writer.save()

#%%
""" Evaluations """

# Sharpe Ratio : average return per unit of volatility
returns = portfolio['returns']
sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())
print("Sharpe Ratio:",sharpe_ratio)

aapl_returns = np.log(aapl[['Adj Close']] / aapl[['Adj Close']].shift(1))
bench_returns = np.log(benchmark[['Adj Close']] / benchmark[['Adj Close']].shift(1))
return_data = pd.concat([bench_returns, aapl_returns], axis=1)[1:]
return_data.columns = ['SPY', 'AAPL']
model = sm.OLS(return_data['AAPL'],
               sm.add_constant(return_data['SPY'].values)).fit()

# Alpha : gauges excess return of investment to that of market
print('Alpha:',model.params[0])
# Beta : measures volatility of investment to entire market
print('Beta:',model.params[1])
# R-Squared : measures how correlated change in prices is to market
print('R-Squared',model.rsquared)

# Compound Annual Growth Rate : constant rate of return over a period
days = (aapl.index[-1] - aapl.index[0]).days
cagr = ((((aapl['Adj Close'][-1]) / aapl['Adj Close'][1])) ** (365.0/days)) - 1
print("CAGR:",cagr)

# Max Drawdown : measures largest drop from peak to bottom, indicates risk
window = 252
rolling_max = aapl['Adj Close'].rolling(window, min_periods=1).max()
daily_drawdown = aapl['Adj Close']/rolling_max - 1.0
max_daily_drawdown = daily_drawdown.rolling(window, min_periods=1).min()
daily_drawdown.plot()
max_daily_drawdown.plot()
plt.show()
