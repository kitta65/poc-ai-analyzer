from pydantic_ai import ModelSettings
from pydantic_ai.models.openai import OpenAIChatModel

MODEL_NAME = "gpt-4.1-mini"
BASE_MODEL = OpenAIChatModel(
    MODEL_NAME,
    # you can override default settings when instantiating the agent
    settings=ModelSettings(temperature=0.8, max_tokens=500),
)

CUBE_API = "http://localhost:4000/cubejs-api"