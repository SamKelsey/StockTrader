from bs4 import BeautifulSoup
import requests, json

# Returns list of most active stock tickers from Yahoo Finance
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

# Accepts json response object and returns pandas df
def createDF(r):
    response = json.loads(r.text)
    print(response)