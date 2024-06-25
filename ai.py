import requests
from content import Content, ContentType
from message import Message, Role

api_key = "sk-proj-BE8OgmDpTABgJJpmnWhIT3BlbkFJwgm7Zt9jYa6wyGacJVx4"

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

def getResponse(payload):
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
      response_data = response.json()
      answer = response_data['choices'][0]['message']['content']
      return answer
    
    else:
      print(f"Request failed with status code {response.status_code}: {response.text}")

def convert_airesponse_toMessage(response):
   text_content = Content(content_type=ContentType.TEXT, value = response)
   message = Message(role=Role.SYSTEM, content=[text_content])
   return message