from content import Content, ContentType
from message import Message, Role
from payload import Payload
from model import Model
import ai as AI
from tickerDataHelper import get_Classic_Fibonacci, trigger_1d_5min, getTickerImagePath


# Example usage:
# text_content = Content(content_type= ContentType.TEXT, value="Analyze the image")
# image_content = Content(content_type=ContentType.IMAGE_URL, value="my-stock-app/AAPL_Chart.png")

# message = Message(role=Role.USER, content=[text_content, image_content])

# payload = Payload(model=Model.GPT4o, messages=[message])

# answer = AI.getResponse(payload=payload.getJson())
# print(answer)
stockname = "ZOMATO.NS"
a = get_Classic_Fibonacci("RELIANCE.NS", "1d", "5m")

trigger_1d_5min(stockname)
image_path = getTickerImagePath(stockname, "5m")
text_content = Content(content_type= ContentType.TEXT, value=f'Please analyze the candlestick chart and additional indicators shown in the image for the stock {stockname}. Focus specifically on intraday trading patterns.e')
image_content = Content(content_type=ContentType.IMAGE_URL, value=image_path)
message = Message(role=Role.USER, content=[text_content, image_content])
payload = Payload(model=Model.GPT4o, messages=[message])
answer = AI.getResponse(payload=payload.getJson())
print(answer)

