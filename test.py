from analyzable_stock import AnalyzableStock
from multithreading import generate_all_charts_for_stock
from prompt import PrompText
import tickerDataHelper as tickerHelper
from content import Content, ContentType
import json

import ai_analysis
#Uncomment below line to analyze a stock
stock = AnalyzableStock("ZOMATO.NS")
stock.analyse()
print(f'stock entry point : {stock.entry_point}')
print(f'stock stop loss : {stock.stop_loss}')
print(f'stock target point : {stock.target_point}')
print(f'stock analysis : {stock.analysis}')
print(f'stock rating : {stock.rating}')

# a = tickerHelper.get_stock_data("RELIANCE.NS", "1d", "5m")
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
