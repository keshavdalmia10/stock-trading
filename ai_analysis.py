import tickerDataHelper as tickerHelper
from content import Content, ContentType
from message import Message, Role
from payload import Payload
from model import Model
from prompt import PrompText
import ai as AI
from stock import Stock
import tickerDataHelper as tickerHelper
import json
from multithreading import generate_all_charts_for_stock

def imageanalysis(stock : Stock):
    stockname = stock.stock_name
    tickerHelper.trigger_1d_15min(stockname)
    tickerHelper.trigger_1d_5min(stockname)
    tickerHelper.trigger_5d_60min(stockname)
    
    image_path_5d_60min = tickerHelper.getTickerImagePath(stockname, "60m")
    image_path_15min = tickerHelper.getTickerImagePath(stockname, "15m")
    image_path_5min = tickerHelper.getTickerImagePath(stockname, "5m")

    initial_image_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.INITIAL_IMAGE_ANALYSIS.format(tickername = stockname))
    image_5d_60min = Content(content_type=ContentType.IMAGE_URL, value= image_path_5d_60min)
    image_15min = Content(content_type=ContentType.IMAGE_URL, value= image_path_15min)
    image_5min = Content(content_type=ContentType.IMAGE_URL, value= image_path_5min)

    message = Message(role=Role.USER, content=[initial_image_analysis_text, image_5d_60min, image_15min, image_5min])
    
    transformed_message = Message(role=Role.USER, content=[initial_image_analysis_text])

    stock.add_in_history(transformed_message)
    payload = Payload(model=Model.GPT4o, messages=[message])
    answer = AI.getResponse(payload=payload.getJson())
    stock.image_analysis = answer
    
    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)
    

def jsonAnalysis(stock : Stock):
    fibonacciString30min = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "1d", "30m")

    json_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.JSON_ANALYSIS.value)

    json_text30min = Content(content_type=ContentType.TEXT, value= json.dumps(fibonacciString30min))

    message = Message(role=Role.USER, content=[json_analysis_text, json_text30min])
    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.json_analysis = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)

def indicatorAnalysis(stock : Stock):
    indicator_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.INDICATOR_ANALYSIS.value)
    message = Message(role=Role.USER, content=[indicator_analysis_text])

    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.indicator_analysis = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)

def tradingStrategy(stock : Stock):
    trading_strategy_text = Content(content_type= ContentType.TEXT, value=PrompText.TRADING_STRATEGY.value)
    message = Message(role=Role.USER, content=[trading_strategy_text])

    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.trading_strategy = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)
    
def fullAnalysis(stock : Stock):
    imageanalysis(stock)
    jsonAnalysis(stock)
    indicatorAnalysis(stock)
    tradingStrategy(stock)
