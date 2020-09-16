from methods import Alpaca_API_methods as API, data_methods as myData
import datetime as dt
from pathlib import Path
import pandas as pd
import os
import time
import math

cwd = os.getcwd()  # Current Working Directory

# Update Alpaca Watchlist and ticker .csv files every Monday
if dt.datetime.today().weekday() == 0:
    # Get most volatile stocks and add them to Alpaca watchlist
    tickers = myData.findStocks()
    watchlistTickers = API.getWatchlistTickers()
    newTickers = []
    for ticker in tickers:
        if ticker in watchlistTickers:  # Check if ticker already in watchlist
            continue
        else:
            API.addToWatchlist(ticker)  # Add ticker to watchlist
            newTickers.append(ticker)

    # Remove tickers if they not in new yahoo list and we don't own any of their stock
    for watchListTicker in watchlistTickers:
        if (watchListTicker not in tickers) and (API.checkPositionQty(watchListTicker) == 0):
            API.removeFromWatchlist(watchListTicker)

            # Remove old ticker csv files
            relativePath = "/packages/methods/ticker_data/"
            pathString = cwd + relativePath + watchListTicker + ".csv"
            path = Path(pathString)
            os.remove(path)

    # Perform GET request for new tickers
    response = API.getTickerInfo(newTickers, 10)

    # Convert GET response into dictionary of df's
    dfDict = myData.createDF(response)

    # Write df's to individual ticker csv files in ticker_data folder
    myData.createDataFiles(dfDict)

# List of tickers to watch & minute interval between checks
tickers = API.getWatchlistTickers()

# Interval between data checks
INTERVAL = 5

timeNow = dt.datetime.now().time()  # Current time
timeOpen = dt.time(14, 30, 00)  # NASDAQ Open time
timeClose = dt.time(22, 00, 00)  # NASDAQ Close time

while (timeNow > timeOpen) and (timeNow < timeClose):
    print("running...")

    # Update ticker's csv files
    myData.updateTickerData(tickers)

    # Iterate through list of currently watched tickers
    for ticker in tickers:

        # Read ticker csv file into a df
        relativePath = "/packages/methods/ticker_data/"
        pathString = cwd + relativePath + ticker + ".csv"
        path = Path(pathString)
        tickerDf = pd.read_csv(path)

        QTY = math.ceil(500 / tickerDf['Close'].iloc[-1])

        # Determine whether to buy/sell latest index row of ticker df
        result = myData.buyOrSell(ticker, tickerDf, -1)
        if result == 1:  # Buy stocks of ticker
            API.buyStock(ticker, QTY)
        elif result == 2:  # Sell stocks of ticker
            API.sellStock(ticker, QTY)

    time.sleep(60*INTERVAL)
