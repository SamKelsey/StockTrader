from Stock import Stock
from methods import Alpaca_API_methods as API, data_methods as myData
from datetime import datetime as dt
from pathlib import Path
import pandas as pd
import os
import time

if dt.today().weekday() == 0:  # Update watchlist every monday (TODO - Method of handling purchased stocks that need removed)
    # Get most volatile stocks and add them to Alpaca watchlist
    tickers = myData.findStocks()
    watchlistTickers = API.getWatchlistTickers()
    for ticker in tickers:
        if ticker in watchlistTickers:  # Check if ticker already in watchlist
            continue
        else:
            API.addToWatchlist(ticker)  # Add ticker to watchlist

# Example list of tickers and quantity to buy/sell each time
tickers = ['AMZN', 'TSLA']
QTY = 1
INTERVAL = 5

# Perform GET request for all tickers
response = API.getTickerInfo(tickers, 10)

# Convert GET response into dictionary of df's
dfDict = myData.createDF(response)

# Write df's to individual ticker csv files in ticker_data folder
myData.createDataFiles(dfDict)

# ENTER WHILE LOOP HERE !!!!!

cwd = os.getcwd()  # Current Working Directory

# Update ticker's csv files
myData.updateTickerData(tickers)

# Iterate through list of currently watched tickers
for ticker in tickers:

    # Read ticker csv file into a df
    relativePath = "/packages/methods/ticker_data/"
    pathString = cwd + relativePath + ticker + ".csv"
    path = Path(pathString)
    tickerDf = pd.read_csv(path)

    # Determine whether to buy/sell latest index row of ticker df
    result = myData.buyOrSell(ticker, tickerDf, -1)

    if result == 1:  # Buy stocks of ticker
        API.buyStock(ticker, QTY)
    elif result == 2:  # Sell stocks of ticker
        API.sellStock(ticker, QTY)

time.sleep(60*INTERVAL)
