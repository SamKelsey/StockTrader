from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from methods import Alpaca_API_methods as API
from methods.API_info import LIMIT

# Accepts dictionary of dataframes and converts each to a csv named by ticker


def createDataFiles(dfDict):
    for ticker in dfDict:
        df = dfDict[ticker]
        cwd = os.getcwd()
        relativePath = "/packages/methods/ticker_data/"
        pathString = cwd + relativePath + ticker + ".csv"
        path = Path(pathString)
        df.to_csv(path)


# Determines to buy or sell for a specified row index of a ticker df
# Accepts a ticker, df and df index. Returns 1->Buy, 2->Sell, 0->No action
def buyOrSell(ticker, df, i):
    if df['Middle'].iloc[i] < df['Long'].iloc[i] and df['Short'].iloc[i] < df['Middle'].iloc[i] and df['LongChange'].iloc[i] > 0 and df['flagLong'].iloc[i] == False and df['flagShort'].iloc[i] == False:
        # Update flag value
        df['flagShort'].iloc[i] = True

        # Update df to csv file
        dfDict = {ticker: df}
        createDataFiles(dfDict)

        return 1  # BUY
    elif df['flagShort'].iloc[i] == True and df['Short'].iloc[i] > df['Middle'].iloc[i]:
        # Update flag value
        df['flagShort'].iloc[i] = False

        # Update df to csv file
        dfDict = {ticker: df}
        createDataFiles(dfDict)

        return 2  # SELL
    elif df['Middle'].iloc[i] > df['Long'].iloc[i] and df['Short'].iloc[i] > df['Middle'].iloc[i] and df['flagLong'].iloc[i] == False and df['flagShort'].iloc[i] == False:
        # Update flag value
        df['flagLong'].iloc[i] = True

        # Update df to csv file
        dfDict = {ticker: df}
        createDataFiles(dfDict)

        return 1  # BUY
    elif df['flagLong'].iloc[i] == True and df['Short'].iloc[i] < df['Middle'].iloc[i]:
        # Update flag value
        df['flagLong'].iloc[i] = False

        # Update df to csv file
        dfDict = {ticker: df}
        createDataFiles(dfDict)

        return 2  # SELL
    elif i == 0:  # If it's the first index just set it to false
        df['flagLong'] = False
        df['flagShort'] = False

        # Update df to csv file
        dfDict = {ticker: df}
        createDataFiles(dfDict)

        return 0  # NO ACTION

# Returns list of most active stock tickers from Yahoo Finance


def findStocks():
    link = "https://finance.yahoo.com/most-active/"
    r = requests.get(url=link)
    soup = BeautifulSoup(r.content, 'lxml')
    tableRows = soup.find('table', {'class': 'W(100%)'}).find(
        'tbody').find_all('tr')
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

        df['flagLong'] = False
        df['flagShort'] = False

        # Rename columns
        df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume'
        }, inplace=True)

        # Calculate short, medium and long exponential moving averages
        shortSpan = LIMIT/200
        middleSpan = LIMIT/10
        longSpan = LIMIT/2
        # span=5 is the original
        ShortEMA = df.Close.ewm(span=shortSpan, adjust=False).mean()
        MiddleEMA = df.Close.ewm(
            span=middleSpan, adjust=False).mean()  # span=21
        LongEMA = df.Close.ewm(span=longSpan, adjust=False).mean()  # span=63

        # Add exponential moving averages to df
        df['Short'] = ShortEMA
        df['Middle'] = MiddleEMA
        df['Long'] = LongEMA
        df['LongChange'] = df['Long'].pct_change()

        dfDict[ticker] = df

    return dfDict


# Accepts list of tickers and updates the csv files with most recent info and removes most outdated info


def updateTickerData(tickers):

    r = API.getTickerInfo(tickers, 1)
    response = json.loads(r.content)
    for ticker in response:
        df = pd.DataFrame.from_dict(response[ticker])

        # Convert time unit
        df['t'] = pd.to_datetime(df['t'], unit='s')

        # Set time as index and remove index name
        df.set_index('t', inplace=True)
        df.index.name = None

        # Rename columns
        df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume'
        }, inplace=True)

        # Read original csv
        cwd = os.getcwd()
        path = Path(cwd + "/packages/methods/ticker_data/" + ticker + ".csv")
        dfOld = pd.read_csv(path, index_col=0)

        df['flagShort'] = dfOld['flagShort'].iloc[-1]
        df['flagLong'] = dfOld['flagLong'].iloc[-1]

        # Check for duplicate index's
        indexString1 = str(df.index[0])
        indexString2 = dfOld.index[-1]

        if indexString1 == indexString2:
            continue

        # Add new info to end
        dfNew = dfOld.append(df)

        # Remove oldest info (first row)
        dfNew = dfNew.iloc[1:, ]

        # Calculate short, medium and long exponential moving averages
        shortSpan = LIMIT/200
        middleSpan = LIMIT/10
        longSpan = LIMIT/2
        # span=5 is the original
        ShortEMA = dfNew.Close.ewm(span=shortSpan, adjust=False).mean()
        MiddleEMA = dfNew.Close.ewm(
            span=middleSpan, adjust=False).mean()  # span=21
        LongEMA = dfNew.Close.ewm(
            span=longSpan, adjust=False).mean()  # span=63

        # Add exponential moving averages to df
        dfNew['Short'] = ShortEMA
        dfNew['Middle'] = MiddleEMA
        dfNew['Long'] = LongEMA
        dfNew['LongChange'] = dfNew['Long'].pct_change()

        # Write to csv file under same name
        dfNew.to_csv(path)
