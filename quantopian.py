#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 20:29:48 2020

@author: maviszeng

This code can either be run on Quantopian online or with zipline and Quandl
remotely.
"""

from zipline.api import order, order_target, record, symbol, log

"""
Quantopian example: a simple momentum script, buy when the stock goes up 
quickly and sell when it goes down.  
"""

def initialize(context):
    context.security = symbol('AAPL')

def handle_data(context, data):
    # moving average for the last 5 days and its current price. 
    average_price = data[context.security].mavg(5)
    current_price = data[context.security].price
    # calculate the current amount of cash in our portfolio.   
    cash = context.portfolio.cash

    if current_price > 1.01*average_price and cash > current_price:
        # how many shares we can buy
        number_of_shares = int(cash/current_price)
        # buy order
        order(context.security, +number_of_shares)
        log.info("Buying %s" % (context.security.symbol))
    elif current_price < average_price:
        # sell all of our shares
        order_target(context.security, 0)
        log.info("Selling %s" % (context.security.symbol))

    # record the Apple stock price.
    record(stock_price=data[context.security].price)

