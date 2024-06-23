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

def imageanalysis(stock : Stock):
    stockname = stock.stock_name
    tickerHelper.trigger_1d_15min(stockname)
    tickerHelper.trigger_1d_5min(stockname)
    tickerHelper.trigger_1d_1min(stockname)
    
    image_path_1min = tickerHelper.getTickerImagePath(stockname, "1m")
    image_path_15min = tickerHelper.getTickerImagePath(stockname, "15m")
    image_path_5min = tickerHelper.getTickerImagePath(stockname, "5m")

    initial_image_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.INITIAL_IMAGE_ANALYSIS.format(tickername = stockname))
    image_1min = Content(content_type=ContentType.IMAGE_URL, value= image_path_1min)
    image_15min = Content(content_type=ContentType.IMAGE_URL, value= image_path_15min)
    image_5min = Content(content_type=ContentType.IMAGE_URL, value= image_path_5min)

    message = Message(role=Role.USER, content=[initial_image_analysis_text, image_1min, image_15min, image_5min])
    stock.add_in_history(message)
    payload = Payload(model=Model.GPT4o, messages=stock.message_history)
    answer = AI.getResponse(payload=payload.getJson())
    stock.image_analysis = answer
    
    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)
    

def jsonAnalysis(stock : Stock):
    jsonString1m = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "1d", "1m")
    jsonString5m = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "1d", "5m")
    jsonString15m = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "1d", "15m")

    json_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.JSON_ANALYSIS.value)

    json_text1min = Content(content_type=ContentType.TEXT, value= json.dumps(jsonString1m))
    json_text15min = Content(content_type=ContentType.TEXT, value= json.dumps(jsonString15m))
    json_text5min = Content(content_type=ContentType.TEXT, value= json.dumps(jsonString5m))

    message = Message(role=Role.USER, content=[json_analysis_text, json_text1min, json_text15min, json_text5min])
    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4o, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.json_analysis = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)

def indicatorAnalysis(stock : Stock):
    indicator_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.INDICATOR_ANALYSIS.value)
    message = Message(role=Role.USER, content=[indicator_analysis_text])

    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4o, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.indicator_analysis = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)

def tradingStrategy(stock : Stock):
    trading_strategy_text = Content(content_type= ContentType.TEXT, value=PrompText.TRADING_STRATEGY.value)
    message = Message(role=Role.USER, content=[trading_strategy_text])

    stock.add_in_history(message)

    payload = Payload(model=Model.GPT4o, messages= stock.message_history)

    answer = AI.getResponse(payload=payload.getJson())

    stock.trading_strategy = answer

    converted_ai_message = AI.convert_airesponse_toMessage(answer)

    stock.add_in_history(converted_ai_message)
    
def fullAnalysis(stock : Stock):
    imageanalysis(stock)
    jsonAnalysis(stock)
    indicatorAnalysis(stock)
    tradingStrategy(stock)
