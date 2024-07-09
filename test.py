from analyzable_stock import AnalyzableStock
from multithreading import generate_all_charts_for_stock
from prompt import PrompText
import tickerDataHelper as tickerHelper
from content import Content, ContentType
import json
import datetime
import threading
import trader as trader

import ai_analysis
#Check multithreading
# stocklist = ["ZOMATO.NS", "RELIANCE.NS", "PNB.NS"]
# trader.trade_stocks(stocklist)

#Check if variables are being assigned properly
# stock = AnalyzableStock("ZOMATO.NS")
# stock.analyse()
# print(f'stock entry point : {stock.entry_point}')
# print(f'stock stop loss : {stock.stop_loss}')
# print(f'stock target point : {stock.target_point}')
# print(f'stock analysis : {stock.analysis}')
# print(f'stock rating : {stock.rating}')

# a = tickerHelper.constructTickerImages("RELIANCE.NS", "1d", "5m")
# print(type(a.json()))
# print(a.json())

# stock.analyse()
# stock.analyse()
# print(stock.trading_strategy)
# print(stock.rating)
# stock.rating = 9
# print(stock.rating)
# print(stock.rating)

#Uncomment below line to check chart creation
# generate_all_charts_for_stock("ZOMATO.NS")
# fibonacciString30min = tickerHelper.get_Classic_Fibonacci("RELIANCE.NS", "1d", "30m")
# json_text30min = Content(content_type=ContentType.TEXT, value= json.dumps(fibonacciString30min))
# stock_name = "relaince"

# print(PrompText.USER_PROMPT.format(stockname = stock_name, fibonaci_json = fibonacciString30min))
# stock1 = AnalyzableStock("stock1")
# stock1.testwrite("Rowdy")
# stock2 = AnalyzableStock("stock2")
# stock2.testwrite("Anyting")
# print(stock1.analysis)
# print(stock2.analysis)

def generate_charts_for_stocks(stock_symbols):
    threads = []
    start_time = datetime.datetime.now()
    
    for stock_symbol in stock_symbols:
        thread = threading.Thread(target=generate_all_charts_for_stock, args=(stock_symbol,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = datetime.datetime.now()
    print(end_time - start_time)

# Example usage
stock_symbols = ["ZOMATO.NS", "YESBANK.NS", "RELIANCE.NS", "PNB.NS", "HDFCBANK.NS"]
# stock_symbols = ["ZOMATO.NS"]
generate_charts_for_stocks(stock_symbols)