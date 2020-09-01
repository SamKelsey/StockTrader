from Stock import Stock
from methods import Alpaca_API_methods as API, data_methods as myData

response = API.getTickerInfo(["AMZN", "TSLA"], 1)
myData.createDF(response)


