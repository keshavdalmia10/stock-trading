# content.py

from typing import Dict, Any
from enum import Enum
import base64
import imageProvider as imageProvider

class ContentType(Enum):
    TEXT = "text"
    IMAGE_URL = "image_url"

class Content:
    def __init__(self, content_type: ContentType, value: str):
        self.content_type = content_type
        self.value = value

        valid_content_types = [ctype.value for ctype in ContentType]
        if content_type.value not in valid_content_types:
            raise ValueError(f"INVALID CONTENT TYPE: Content type '{content_type.value}' is invalid. Only types {', '.join(valid_content_types)} are allowed.")

    def to_dict(self):
        if self.content_type == ContentType.TEXT:
            return {'type': self.content_type.value, "text": self.value}
        elif self.content_type == ContentType.IMAGE_URL:
            return {'type': self.content_type.value, "image_url": {"url": imageProvider.create_image_url(self.value)}}


        
    
