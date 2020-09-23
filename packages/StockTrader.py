from methods import Alpaca_API_methods as API, data_methods as myData
import datetime as dt
from pathlib import Path
import pandas as pd
import os
import time
import math

cwd = os.getcwd()  # Current Working Directory

# Update Alpaca Watchlist and ticker .csv files every Monday
if dt.datetime.today().weekday() == 2:
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

    # Check there are new tickers to be added
    if len(newTickers) > 0:
        # Perform GET request for new tickers
        response = API.getTickerInfo(newTickers, 1000)

        if response.status_code == 200:
            # Convert GET response into dictionary of df's
            dfDict = myData.createDF(response)

            # Write df's to individual ticker csv files in ticker_data folder
            myData.createDataFiles(dfDict)

    # Check no stock is already owned of new tickers.
    # If so, set flagLong to True in csv file
    for ticker in newTickers:
        if API.checkPositionQty(ticker) > 0:  # Check qty of ticker owned
            # Open tickers csv into a df
            relativePath = "/packages/methods/ticker_data/"
            pathString = cwd + relativePath + ticker + ".csv"
            path = Path(pathString)
            df = pd.read_csv(path, index_col=0)

            # Set latest flagLong to true
            df['flagLong'].iloc[-1] = True
            print(df['flagLong'].iloc[-1])
            print("Qty: " + str(API.checkPositionQty(ticker)))

            # Re-write to csv file
            df.to_csv(path)


# List of tickers to watch & minute interval between checks
tickers = API.getWatchlistTickers()
print("Today's Watchlist: " + str(tickers))

# Interval between data checks
INTERVAL = 5

timeNow = dt.datetime.now().time()  # Current time
timeOpen = dt.time(14, 30, 00)  # NASDAQ Open time
timeClose = dt.time(21, 30, 00)  # NASDAQ Close time

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
        tickerDf = pd.read_csv(path, index_col=0)

        QTY = math.ceil(500 / tickerDf['Close'].iloc[-1])

        # Determine whether to buy/sell latest index row of ticker df
        result = myData.buyOrSell(ticker, tickerDf, -1)
        # Buy stocks of ticker if none already owned
        if result == 1 and API.checkPositionQty(ticker) == 0:
            API.buyStock(ticker, QTY)
        elif result == 2:  # Sell stocks of ticker
            API.sellStock(ticker, QTY)

    time.sleep(60*INTERVAL)
