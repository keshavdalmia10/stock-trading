import trader as trader
import datetime
import time
startTime = datetime.datetime.now()
print(startTime)
stocklist = ["ZOMATO.NS", "RELIANCE.NS", "PNB.NS", "IDEA.NS", "YESBANK.NS", "INDUSTOWER.NS", "SAIL.NS", "BHEL.NS"]
trader.trade_stocks(stocklist)
endTime = datetime.datetime.now()
print(endTime)
print(f'Time taken to execute : {endTime - startTime}')