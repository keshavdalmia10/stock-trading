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
import json
import logging
logger = logging.getLogger(__name__)

def imageanalysis(stock : Stock):
    stockname = stock.stock_name

    generate_all_charts_for_stock(stockname)
    
    image_path_5d_60min = tickerHelper.getTickerImagePath(stockname, "60m")
    image_path_15min = tickerHelper.getTickerImagePath(stockname, "15m")
    image_path_5min = tickerHelper.getTickerImagePath(stockname, "5m")

    initial_image_analysis_text = Content(content_type= ContentType.TEXT, value=PrompText.INITIAL_IMAGE_ANALYSIS.value)
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

    
def chained_analysis(stock : Stock):
    imageanalysis(stock)
    jsonAnalysis(stock)
    indicatorAnalysis(stock)
    tradingStrategy(stock)

def two_chain_analysis(stock : Stock):
    imageanalysis(stock)
    all_in_one(stock)

def all_in_one(stock : Stock):
    stock_name = stock.stock_name
    fibonacciString30min = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "1d", "30m")

    system_text = Content(content_type= ContentType.TEXT, value=PrompText.SYSTEM_PROMPT.value)
    system_message = Message(role=Role.SYSTEM, content=[system_text])

    initial_user_text = Content(content_type= ContentType.TEXT, value=PrompText.USER_QUESTION.value)
    example_user_message = Message(role=Role.USER, content=[initial_user_text])

    assistant_response_text = Content(content_type= ContentType.TEXT, value=PrompText.ASSISTANT_ANSWER.value)
    example_assistant_message = Message(role=Role.ASSISTANT, content=[assistant_response_text])


    generate_all_charts_for_stock(stock_name)
    image_path_5d_60min = tickerHelper.getTickerImagePath(stock_name, "60m")
    image_path_15min = tickerHelper.getTickerImagePath(stock_name, "15m")
    image_path_5min = tickerHelper.getTickerImagePath(stock_name, "5m")
    image_5d_60min = Content(content_type=ContentType.IMAGE_URL, value= image_path_5d_60min)
    image_5d_15min = Content(content_type=ContentType.IMAGE_URL, value= image_path_15min)
    image_5min = Content(content_type=ContentType.IMAGE_URL, value= image_path_5min)

    stock_trading_data_5m_1d = tickerHelper.get_stock_data(stock_name, "1d", "5m")

    user_prompt_text = Content(content_type= ContentType.TEXT, value=PrompText.USER_PROMPT.format(stockname = stock_name, fibonaci_json = fibonacciString30min, stock_data = stock_trading_data_5m_1d ))
    user_message = Message(role=Role.USER, content=[image_5d_60min, image_5d_15min, image_5min, user_prompt_text])

    payload = Payload(model=Model.GPT4o, messages= [system_message, example_user_message, example_assistant_message, user_message])
    
    answer = AI.getResponse(payload=payload.getJson())
    
    stock.writejson(answer)
    # tickerHelper.delete_all_generated_images(stock_name)

def candlestick_volume_analysis(stock : Stock):
    stock_name = stock.stock_name
    fibonacciString5d_30min = tickerHelper.get_Classic_Fibonacci(stock.stock_name, "5d", "30m")

    system_text = Content(content_type= ContentType.TEXT, value=PrompText.SYSTEM_PROMPT.value)
    system_message = Message(role=Role.SYSTEM, content=[system_text])

    initial_user_text = Content(content_type= ContentType.TEXT, value=PrompText.USER_QUESTION.value)
    example_user_message = Message(role=Role.USER, content=[initial_user_text])

    assistant_response_text = Content(content_type= ContentType.TEXT, value=PrompText.ASSISTANT_ANSWER.value)
    example_assistant_message = Message(role=Role.ASSISTANT, content=[assistant_response_text])

    generate_all_charts_for_stock(stock_name)

    image_path_1d_15min = tickerHelper.getTickerImagePath(stock_name, "15m")
    image_path_1d_5min = tickerHelper.getTickerImagePath(stock_name, "5m")
    image_path_1mo_1d = tickerHelper.getTickerImagePath(stock_name, "1d")
    image_1d_15min = Content(content_type=ContentType.IMAGE_URL, value= image_path_1d_15min)
    image_1d_5min = Content(content_type=ContentType.IMAGE_URL, value= image_path_1d_5min)
    image_1mo_1d = Content(content_type=ContentType.IMAGE_URL, value= image_path_1mo_1d)

    user_prompt_text = Content(content_type= ContentType.TEXT, value=PrompText.USER_PROMPT.format(stockname = stock_name, fibonaci_json = fibonacciString5d_30min))

    user_message = Message(role=Role.USER, content=[image_1d_15min, image_1d_5min, image_1mo_1d, user_prompt_text])

    payload = Payload(model=Model.GPT4o, messages= [system_message, example_user_message, example_assistant_message, user_message])

    answer = AI.getResponse(payload=payload.getJson())
    
    stock.writejson(answer)

    tickerHelper.delete_all_generated_images(stock_name)