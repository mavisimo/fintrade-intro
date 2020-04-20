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

#%%
"""
aapl = pdr.get_data_yahoo('AAPL',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
benchmark = pdr.get_data_yahoo('SPY',start=datetime.datetime(2014, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
"""
""" Moving Average Crossover """
"""  
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
"""
""" Backtesting """
"""
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

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
portfolio['total'].plot(ax=ax1, lw=1)
ax1.plot(portfolio.loc[signals.long_short == 1.0].index, portfolio.total
         [signals.long_short == 1.0], '^', markersize=8, color='m')
ax1.plot(portfolio.loc[signals.long_short == -1.0].index, portfolio.total
         [signals.long_short == -1.0], 'v', markersize=8, color='k')

plt.show()
"""
""" Evaluations """
"""
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
"""
#%%

def initialize(ticker):
    data = pdr.get_data_yahoo(ticker,start=datetime.datetime(2017, 10, 1), 
                          end=datetime.datetime(2020, 1, 1))
    return data
    
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

def diversify(stocks): # list of stocks
    returns = pd.DataFrame(index=stocks[0].index)
    for portfolio in stocks:
        returns['total'] = portfolio['holdings'] + portfolio['cash']
        returns['returns'] = portfolio['total'].pct_change()
    return returns

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
    window = 252
    rolling_max = data['Adj Close'].rolling(window, min_periods=1).max()
    daily_drawdown = data['Adj Close']/rolling_max - 1.0
    max_daily_drawdown = daily_drawdown.rolling(window, min_periods=1).min()
    daily_drawdown.plot()
    max_daily_drawdown.plot()
    plt.show()

def save(ticker, data, signals, portfolio):
    file_name = ticker + '_data.xlsx'
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Yahoo Data')
    signals.to_excel(writer, sheet_name='Strategy')
    portfolio.to_excel(writer, sheet_name='Portfolio')
    writer.save()

def evaluate(ticker,data,benchmark,portfolio):
    returns = portfolio['returns']
    sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())
    print("Sharpe Ratio:",sharpe_ratio)
    data_returns = np.log(data[['Adj Close']] / data[['Adj Close']].shift(1))
    bench_returns = np.log(benchmark[['Adj Close']] / 
                           benchmark[['Adj Close']].shift(1))
    return_data = pd.concat([bench_returns, data_returns], axis=1)[1:]
    return_data.columns = ['Market', ticker]
    model = sm.OLS(return_data[ticker],
               sm.add_constant(return_data['Market'].values)).fit()
    print('Alpha:',model.params[0])
    print('Beta:',model.params[1])
    print('R-Squared',model.rsquared)
    days = (data.index[-1] - data.index[0]).days
    cagr = ((((data['Adj Close'][-1]) / data['Adj Close'][1])) ** 
            (365.0/days)) - 1
    print("CAGR:",cagr)

#%%
ticker = 'AAPL'
data = initialize(ticker)
sp500 = initialize('SPY')
moving_avg = strategy(data,30,120)
portfolio = portfolios(ticker, data, moving_avg, 70, 10000)
backtest(data, moving_avg, portfolio)
save(ticker, data, moving_avg, portfolio)
evaluate(ticker,data,sp500,portfolio)

#%%
tickers = ['AAPL', 'TSLA', 'AMZN', 'GOOG']
stocks = []
for ticker in tickers:
    data = initialize(ticker)
    moving_avg = strategy(data,30,120)
    stocks.append(portfolios(ticker, data, moving_avg, 100, 5000))
returns = diversify(stocks)

sp500 = initialize('SPY')
market_strat = strategy(sp500,30,120)
m_portfolio = portfolios(ticker, sp500, market_strat, 100, 5000)

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
returns['total'].plot(ax=ax1, lw=1, color='r')
m_portfolio['total'].plot(ax=ax1, lw=1)
plt.show()
t_return = returns['returns']
print("Sharpe Ratio:",np.sqrt(252) * (t_return.mean() / t_return.std()))
