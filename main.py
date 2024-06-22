from content import Content, ContentType
from message import Message, Role
from payload import Payload
from model import Model
import ai as AI


# Example usage:
text_content = Content(content_type= ContentType.TEXT, value="Analyze the image")
image_content = Content(content_type=ContentType.IMAGE_URL, value="AAPL_Chart.png")

message = Message(role=Role.USER, content=[text_content, image_content])

payload = Payload(model=Model.GPT4o, messages=[message])

answer = AI.getResponse(payload=payload.getJson())
print(answer)