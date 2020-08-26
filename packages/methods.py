from bs4 import BeautifulSoup
import requests, json

BASE_URL = "https://paper-api.alpaca.markets"
HEADERS = {"APCA-API-KEY-ID":"PKXDRX4PECLPBUUBIRKD", "APCA-API-SECRET-KEY":"j4ZuyEsnJJcEsO1XIbTnPlIp5HaZVVTDD0h8p8Tx"}

# Scrapes Yahoo Finance most active stocks
# Returns list of most active stock tickers
def findStocks():
    link = "https://finance.yahoo.com/most-active/"
    r = requests.get(url = link)
    soup = BeautifulSoup(r.content, 'lxml')
    tableRows = soup.find('table', {'class': 'W(100%)'}).find('tbody').find_all('tr')
    tickersList = []

    for row in tableRows:
        ticker = row.find('td').find('a').text
        tickersList.append(ticker)
    return tickersList

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

