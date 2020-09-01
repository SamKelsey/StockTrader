from bs4 import BeautifulSoup
import requests, json
from methods.API_info import HEADERS, BASE_URL, TIMEFRAME

def getTickerInfo(tickers, qty):
    BASE_URL = "https://data.alpaca.markets"
    endpoint = "/v1/bars/"
    url = BASE_URL + endpoint + TIMEFRAME
    
    # Convert ticker list to string format
    tickerString = ""
    for ticker in tickers:
        tickerString += ticker
        if ticker == tickers[-1]:
            break
        tickerString += ","
    r = requests.get(url, headers=HEADERS, params={"symbols": tickerString, "limit": qty})
    return r

# Returns quantity of stock owned
def checkPositionQty(ticker):
    endpoint = "/v2/positions/"
    url = BASE_URL + endpoint + ticker
    r = requests.get(url, headers=HEADERS)
    statusCode = r.status_code
    response = json.loads(r.text)

    if statusCode == 200:
        return int(response['qty'])
    else:
        return 0   
    
# Buys selected quantity of selected stock
def buyStock(ticker, qty):
    endpoint = "/v2/orders"
    url = BASE_URL + endpoint
    r = requests.post(url, headers=HEADERS, json={'symbol': ticker, 'qty': str(qty), 'side': 'buy', 'type': 'market', 'time_in_force': 'day'})
    # Check status code of order
    if r.status_code == 403:
        print("ERROR: Insufficient funds for purchase")
        return None
    elif r.status_code == 200: 
        print("BUY: " + str(qty) + " shares(s) of " + ticker)
    
# Sells selected quantity of selected stock
def sellStock(ticker, qty):
    # Check account owns enough of stock to sell
    if qty > checkPositionQty(ticker):
        print("ERROR: Insufficient qty of " + ticker + " to sell.")
        return None
    else:
        endpoint = "/v2/orders"
        url = BASE_URL + endpoint
        r = requests.post(url, headers=HEADERS, json={'symbol': ticker, 'qty': str(qty), 'side': 'sell', 'type': 'market', 'time_in_force': 'day'})
        if r.status_code == 200:
            print("SELL: " + str(qty) + " share(s) of " + ticker)

# Creates a watchlist with the given name, filled with the given list of tickers
def createWatchlist(name, tickers):
    endpoint = "/v2/watchlists"
    url = BASE_URL + endpoint
    r = requests.post(url, headers=HEADERS, json={"name": name, "symbols": tickers})
    print(r)
    print(r.text)

# Returns !LIST! of watchlists, each in json
def getWatchlists():
    endpoint = "/v2/watchlists"
    url = BASE_URL + endpoint
    r = requests.get(url, headers=HEADERS)
    return r

# Returns list of tickers in Primary Watchlist
def getWatchlistTickers():
    endpoint = "/v2/watchlists/"
    watchlistID = json.loads(getWatchlists().text)[0]['id']
    url = BASE_URL + endpoint + watchlistID
    r = requests.get(url, headers=HEADERS)
    assets = json.loads(r.text)['assets']
    tickersList = []
    for asset in assets:
        tickersList.append(asset['symbol'])
    return tickersList

# Adds a stock the primary watchlist and returns the response object
def addToWatchlist(ticker):
    endpoint = "/v2/watchlists/"
    watchlistID = json.loads(getWatchlists().text)[0]['id']
    url = BASE_URL + endpoint + watchlistID
    requests.post(url, headers=HEADERS, json={"watchlist_id": watchlistID, "symbol":ticker})

# Removes a stock from the primary watchlist and returns the response object
def removeFromWatchlist(ticker):
    endpoint = "/v2/watchlists/"
    watchlistID = json.loads(getWatchlists().text)[0]['id']
    url = BASE_URL + endpoint + watchlistID + "/" + ticker
    r = requests.delete(url, headers=HEADERS)
    print(r)