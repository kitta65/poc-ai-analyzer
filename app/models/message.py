# see also https://docs.streamlit.io/develop/concepts/design/custom-classes#pattern-1-define-your-class-in-a-separate-module
from enum import Enum
from typing import Any

from pydantic import BaseModel


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(Enum):
    LOG = "log"
    GRAPHQL = "graphql"
    PLAIN = "plain"
    OTHER = "other"


class MessageSchema(BaseModel):
    role: MessageRole
    type: MessageType
    content: Any