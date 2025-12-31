from pydantic_ai import Agent, ModelSettings

from .common import BASE_MODEL


INSTRUCTIONS = f"""\
"""


vegalite_agent = Agent(
    BASE_MODEL,
    model_settings=ModelSettings(),
    instructions=INSTRUCTIONS,
    output_type=str,
)
