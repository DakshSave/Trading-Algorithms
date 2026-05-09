#MEAN-REVERSION TRADING ALGORITHM



#Import Necessary Libraries.
from blueshift.api import (
    symbol,
    order_target_percent,
    schedule_function,
    date_rules,
    time_rules
)
import numpy as np
import pandas as pd



#Initialize Stratgy.
def initialize(context):
    #Define Universe Of Stocks.
    context.assets = [symbol("_"), symbol("_"), symbol("_"), symbol("_")] #Replace Underscores With Desired Stocks' Tickers (Number Of Symbols Can Be Increased Or Decreased Manually).
    #Define Lookback (Rolling) Period.
    context.lookback = _ #Replace Underscore With Desired Lookback Period.
    #Store Portfolio Weights (Initially 0).
    context.prev_weights = pd.Series(0.0, index=context.assets)
    #Schedule Rebalance Function.
    schedule_function(
        rebalance,
        date_rules.every_day(),
        time_rules.market_close(minutes=10)
    )



#Main Trading Logic.
def rebalance(context, data):
    #Fetch Historical Close Prices.
    prices = data.history(context.assets, 'close', context.lookback, '1d')
    #Calculate Percentage Returns.
    returns = prices.pct_change().iloc[-1]
    #Safety Check (Exit If All Returns Are NaN).
    if returns.isnull().all():
        return
    #Calculate Universe Returns (For Benchmarking).
    market_ret = returns.mean()
    #Generate Mean Reversion Signal.
    raw_weights = -(returns - market_ret)
    #Calculate Total Absolute Exposure (To Normalize Portfolio Weights).
    wtsum = np.abs(raw_weights).sum()
    #Safety Check (Exit If Weights Are Invalid Or 0).
    if wtsum == 0 or np.isnan(wtsum):
        return
    #Normalize Weights (Ensures Sum Of Absolute Weights = 1).
    weights = raw_weights / wtsum
    #Calculate Portfolio Turnover (Change In Value Of Portfolio Since Last Rebalance)
    turnover = np.abs(weights - context.prev_weights).sum()
    #Main Long-Short Logic.
    for asset in context.assets:
        #If Weights > 0 Go Long.
        if context.prev_weights[asset] > 0:
            order_target_percent(asset, context.prev_weights[asset])
        #If Weights < 0 Go Short.
        elif context.prev_weights[asset] < 0:
            order_target_percent(asset, context.prev_weights[asset])
        #Else (If Weights = 0) Close Position.  
        else:
            order_target_percent(asset, 0)
    #Store Current Weights For Next Rebalance.
    context.prev_weights = weights.copy()
