from Stock import Stock
from methods import Alpaca_API_methods as API, data_methods as myData
from datetime import datetime as dt

if dt.today().weekday() == 0: # Update watchlist every monday (TODO - Method of handling purchased stocks that need removed)
    # Get most volatile stocks and add them to Alpaca watchlist
    tickers = myData.findStocks()
    watchlistTickers = API.getWatchlistTickers()
    for ticker in tickers:
        if ticker in watchlistTickers: # Check if ticker already in watchlist
            continue
        else:
            API.addToWatchlist(ticker) # Add ticker to watchlist

myData.updateTickerData(['AMZN'])

# Update csv file info
# myData.createDataFiles(myData.createDF(API.getTickerInfo(['AMZN', 'TSLA'], 3)))





