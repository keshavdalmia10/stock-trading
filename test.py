from analyzable_stock import AnalyzableStock
from multithreading import generate_all_charts_for_stock
from prompt import PrompText
import tickerDataHelper as tickerHelper
from content import Content, ContentType
import json
import trader as trader
import model
from ai_strategy import AIStrategyConfig, AIStrategy
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
# stock1 = AnalyzableStock("stock1")
# stock1.testwrite("Rowdy")
# stock2 = AnalyzableStock("stock2")
# stock2.testwrite("Anyting")
# print(stock1.analysis)
# print(stock2.analysis)
print(f'Initial strategy : {AIStrategyConfig.get_strategy()}')
AIStrategyConfig.set_strategy(AIStrategy.GENERATE_AND_USE_CANDLESTICK_GRAPH_AND_PIVOT)
print(f'Changed strategy : {AIStrategyConfig.get_strategy()}')