from typing import Any

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import capture_run_messages, Agent, ModelSettings

from .common import BASE_MODEL
from .logging import logger
from .graphql import run_graphql_agent_with_log
from .vegalite import run_vegalite_agent_with_log
from ..models.vegalite import VegaLiteSchema
from ..cube import get_data_by_query


# TODO: tell the model definitions of Cube
# TODO: tell the agent current date
INSTRUCTIONS = """\
You are an excellent analytics assistant.
Fully understand the user's intent and give instructions to other agents.

If the user's description is ambiguous, ask for additional information.
For example, "I want to visualize the number of active users by day" is not specific enough.
In this case, ask questions like "Do you mean active users as the number of users who placed orders? Or the number of users who generated an event log?"
"""


class RouterSchema(BaseModel):
    graphql: str
    data: list[dict[str, Any]]
    vegalite: VegaLiteSchema


def run_other_agent(
    prompt_for_graphql_agent: str, prompt_for_vegalite_agent: str
) -> RouterSchema:
    """Function to execute other agents"""

    query = run_graphql_agent_with_log(prompt_for_graphql_agent).output
    data = get_data_by_query(query)
    vegalite = run_vegalite_agent_with_log(
        prompt_for_vegalite_agent, pd.DataFrame(data[:5])
    ).output

    return RouterSchema(
        graphql=query,
        data=data,
        vegalite=vegalite,
    )


router_agent = Agent(
    BASE_MODEL,
    model_settings=ModelSettings(),
    instructions=INSTRUCTIONS,
    output_type=run_other_agent,
)


def run_router_agent_with_log(prompt: str):
    with capture_run_messages() as messages:
        try:
            response = router_agent.run_sync(prompt)
        except Exception as e:
            for m in messages:
                logger.error(m)
            raise e

        for m in response.all_messages():
            logger.info(m)
        return response
