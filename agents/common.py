from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.openai import OpenAIChatModel

MODEL_NAME = "gpt-4.1-mini"
BASE_MODEL = OpenAIChatModel(
    MODEL_NAME, settings=ModelSettings(temperature=0.8, max_tokens=500)
)