# payload.py

from typing import List, Dict, Any
from message import Message
from model import Model

class Payload:
    def __init__(self, model: Model, messages: List[Message]):
        self.model = model
        self.messages = messages

        valid_models = [m.value for m in Model]
        if model.value not in valid_models:
            raise ValueError(f"INVALID MODEL: Model '{model.value}' is invalid. Only models {', '.join(valid_models)} are allowed.")

    def to_dict(self):
        response_dict = {
            'model': self.model.value,
            'messages': [m.to_dict() for m in self.messages]
        }

        if self.model.value != Model.GPT4.value:
            response_dict['response_format'] = {"type": "json_object"}

        return response_dict
    
    def getJson(self):
        return self.to_dict()
