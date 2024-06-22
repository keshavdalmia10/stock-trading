# message.py

from typing import List, Dict, Any
from enum import Enum
from content import Content

class Role(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"

class Message:
    def __init__(self, role: Role, content: List[Content]):
        self.role = role
        self.content = content

        valid_roles = [role.value for role in Role]
        if role.value not in valid_roles:
            raise ValueError(f"INVALID ROLE: Role '{role.value}' is invalid. Only roles {', '.join(valid_roles)} are allowed.")

    def to_dict(self):
        return {
            'role': self.role.value,
            'content': [c.to_dict() for c in self.content]
        }
