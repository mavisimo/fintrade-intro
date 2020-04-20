#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 20:29:48 2020

@author: maviszeng

This code can either be run on Quantopian online or with zipline and Quandl
remotely.
"""

from zipline.api import order, order_target, record, symbol, log

#%%
"""
Quantopian start: a simple momentum script, buy when the stock goes up 
quickly and sell when it goes down.  
"""

def initialize(context):
    context.security = symbol('AAPL')

def handle_data(context, data):
    # moving average for long and short window
    MA1 = data[context.security].mavg(30)
    MA2 = data[context.security].mavg(120)
    current_price = data[context.security].price
    current_positions = context.portfolio.positions[symbol('AAPL')].amount
    # calculate the current amount of cash in our portfolio.   
    cash = context.portfolio.cash

    if (MA1>MA2) and current_positions == 0:
        # how many shares we can buy
        number_of_shares = int(cash/current_price)
        # buy order
        order(context.security, +number_of_shares)
        log.info("Buying %s" % (context.security.symbol))
    elif (MA1<MA2) and current_positions != 0:
        # sell all of our shares
        order_target(context.security, 0)
        log.info("Selling %s" % (context.security.symbol))

    # record the Apple stock price and moving averages
    record(MA1=MA1, MA2=MA2, price=current_price)

#%%
    
    