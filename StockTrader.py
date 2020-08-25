from bs4 import BeautifulSoup
import requests

def findStocks():
    link = "https://finance.yahoo.com/most-active/"
    r = requests.get(url = link)
    soup = BeautifulSoup(r.content, 'lxml')
    tableRows = soup.find('table', {'class': 'W(100%)'}).find('tbody').find_all('tr')
    for row in tableRows:
        ticker = row.find('td').find('a')
        print(ticker.text)
        

findStocks()