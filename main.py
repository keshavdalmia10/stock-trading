import trader as trader
import datetime

startTime = datetime.datetime.now()

# stocklist = ["ZOMATO.NS", "RELIANCE.NS", "PNB.NS", "IDEA.NS", "YESBANK.NS", "INDUSTOWER.NS", "SAIL.NS", "BHEL.NS"]
stocklist = ["ZOMATO.NS"]
trader.trade_stocks(stocklist)


endTime = datetime.datetime.now()
print(f'Time taken to execute : {endTime - startTime}')