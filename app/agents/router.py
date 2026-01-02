from typing import Any, Sequence
from datetime import datetime

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import capture_run_messages, Agent, ModelSettings, ModelMessage

from .common import BASE_MODEL
from .logging import logger
from .graphql import run_graphql_agent_with_log
from .vegalite import run_vegalite_agent_with_log
from ..models.vegalite import VegaLiteSchema
from ..cube import get_data_by_query, MODEL_CODE_BLOCKS


INSTRUCTIONS = f"""\
You are an excellent analytics assistant.
Fully understand the user's intent and give instructions to other agents.
You will work with the following two agents:

1. GraphQL Agent: This agent generates a GraphQL query to retrieve data from the Cube backend.
2. VegaLite Agent: This agent generates a Vega-Lite specification to visualize the data retrieved by the GraphQL query.

Other agents cannot reference past interactions. You need to give instructions to other agents based on past interactions.
The user may give instructions based on past interactions.
For example, after an instruction like "Show me weekly unique users who placed orders", they might follow up with "Break that down by gender". In this case, for the second instruction, you need to instruct other agents to "Show me weekly unique users who placed orders, broken down by gender".

If the user's description is ambiguous, ask for additional information.
For example, "I want to visualize the number of active users by day" is not specific enough.
In this case, ask questions like "Do you mean active users as the number of users who placed orders? Or the number of users who generated an event log?"

If the user's desired aggregation is not possible, please decline the request.
There is no way to aggregate metrics other than those defined in the Cube model.
The Cube model definitions are as follows:

{"\n".join(MODEL_CODE_BLOCKS)}

If the user does not specify a period, use the most recent year as the aggregation period.
Always use the tool to get the current date.
"""


class UnableToProceedRequest(BaseModel):
    """Schema to indicate that the agent is unable to proceed with the request (e.g. insufficient information)"""

    reason: str


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
    output_type=[run_other_agent, UnableToProceedRequest],
)


@router_agent.tool_plain
def get_current_date() -> str:
    """Get the current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


def run_router_agent_with_log(prompt: str, history: Sequence[ModelMessage] = []):
    with capture_run_messages() as messages:
        try:
            response = router_agent.run_sync(prompt, message_history=history)
        except Exception as e:
            for m in messages:
                logger.error(m)
            raise e

        for m in response.all_messages():
            logger.info(m)
        return response
