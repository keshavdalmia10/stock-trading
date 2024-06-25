from content import Content, ContentType
from message import Message, Role
from payload import Payload
from model import Model
import ai as AI
from tickerDataHelper import get_Classic_Fibonacci, trigger_1d_5min, getTickerImagePath
import json

# Example usage:
# text_content = Content(content_type= ContentType.TEXT, value="Analyze the image")
# image_content = Content(content_type=ContentType.IMAGE_URL, value="my-stock-app/AAPL_Chart.png")

# message = Message(role=Role.USER, content=[text_content, image_content])

# payload = Payload(model=Model.GPT4o, messages=[message])

# answer = AI.getResponse(payload=payload.getJson())
# print(answer)
stockname = "ZOMATO.NS"
fibonaci = get_Classic_Fibonacci("RELIANCE.NS", "1d", "5m")
fibonaci_text = json.dumps(fibonaci)
# print(type(json.dumps(fibonaci)))
# print(fibonaci)
text_content = Content(content_type=ContentType.TEXT, value = """Analyze the json data of a stock and provide answer in JSON structure like this {"title": {},"answer": {}}""")
f_content = Content(content_type=ContentType.TEXT, value = fibonaci_text)
message = Message(role=Role.USER, content=[text_content,f_content])
payload = Payload(model=Model.GPT4o, messages=[message])
# print(payload.getJson())
answer = AI.getResponse(payload=payload.getJson())
# print(answer)

