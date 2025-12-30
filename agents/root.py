from pydantic_ai import Agent, ModelSettings
from .common import BASE_MODEL


INSTRUCTIONS = """\
Your role is to have fun conversations with the user.
"""


def get_root_agent():
    return Agent(
        BASE_MODEL,
        # you can override settings here
        model_settings=ModelSettings(),
        instructions=INSTRUCTIONS,
    )
