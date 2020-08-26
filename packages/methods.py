from bs4 import BeautifulSoup
import requests

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

# Buys selected quantity of selected stock
def buyStock(ticker, qty):
    endpoint = "/v2/orders"
    url = BASE_URL + endpoint
    requests.post(url, headers=HEADERS, json={'symbol': ticker, 'qty': str(qty), 'side': 'buy', 'type': 'market', 'time_in_force': 'day'})
    print("BUY: " + str(qty) + " shares(s) of " + ticker)

# Sells selected quantity of selected stock
def sellStock(ticker, qty):

    endpoint = "/v2/orders"
    url = BASE_URL + endpoint
    requests.post(url, headers=HEADERS, json={'symbol': ticker, 'qty': str(qty), 'side': 'sell', 'type': 'market', 'time_in_force': 'day'})
    print("SELL: " + str(qty) + " share(s) of " + ticker)
