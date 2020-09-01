from bs4 import BeautifulSoup
import requests, json, pandas as pd

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

# Accepts json response object and returns dict of pandas dataframes by ticker name
def createDF(r):
    response = json.loads(r.text)

    # Convert response object into dictionary of df's by ticker name
    dfDict = {}
    for ticker in response:
        df = pd.DataFrame.from_dict(response[ticker])

        # Convert time unit
        df['t'] = pd.to_datetime(df['t'], unit='s')

        # Set time as index and remove index name
        df.set_index('t', inplace=True)
        df.index.name = None

        # Rename columns
        df.rename(columns={
            'o':'Open',
            'h':'High',
            'l':'Low',
            'c':'Close',
            'v':'Volume'
            }, inplace=True)

        dfDict[ticker] = df

    return dfDict

