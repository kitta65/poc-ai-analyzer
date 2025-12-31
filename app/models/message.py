# see also https://docs.streamlit.io/develop/concepts/design/custom-classes#pattern-1-define-your-class-in-a-separate-module
from pydantic import BaseModel
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(Enum):
    JSON = "json"
    MESSAGE = "message"
    GRAPHQL = "graphql"


class MessageSchema(BaseModel):
    role: MessageRole
    type: MessageType
    content: str