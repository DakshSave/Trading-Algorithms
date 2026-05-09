#Import Necessary Libraries.
from blueshift.api import (
    symbol,
    order_target_percent,
    record,
    schedule_function,
    date_rules,
    time_rules
)
import numpy as np



#Initialize Strategy.
def initialize(context):
    #Create Universe Of Stocks.
    context.assets = [symbol("_"), symbol("_"), symbol("_"), symbol("_")] #Replace Underscores With Desired Stocks' Tickers (Symbols)
    #Define Lookback (Rolling) Window.
    context.window = _ #Replace Underscore With Desired Lookback Period.
    #Define Entry Z-Score.
    context.entry_z = _ #Replace Underscore With Desired Entry Z-Score.
    #Define Exit Z-Score.
    context.exit_z = _ #Replace Underscore With Desired Exit Z-Score.
    #Assign Equal Portfolio Weeight To Each Asset.
    context.weight = 1.0 / len(context.assets)
    #Schedule Trdaing Function.
    schedule_function(trade, date_rules.every_day(), time_rules.market_open())



#Main Trading Logic.
def trade(context, data):
    #Loop Through Universe.
    for asset in context.assets:
        #Fetch Historical Close Prices.
        prices = data.history(asset, 'close', context.window, '1d')
        #Safety Check (Skip Asset If No Data).
        if prices is None or prices.empty:
            continue
        #Calculate Daily Percentage Returns.
        returns = prices.pct_change().dropna()
        #Calculate Rolling Mean Returns.
        mean = returns.mean()
        #Calculate Rolling Standard Deviation Of Returns.
        std = returns.std()
        #Safety Check (Avoid Division By 0).
        if std == 0:
            continue
        #Calculate Z-Score.
        z = (returns.iloc[-1] - mean) / std

        if z >= context.entry_z:
            order_target_percent(asset, context.weight)

        elif z <= -context.entry_z:
            order_target_percent(asset, -context.weight)

        elif abs(z) <= context.exit_z:
            order_target_percent(asset, 0.0)
