from graphql import (
    build_client_schema,
    get_introspection_query,
    validate,
    parse,
    print_schema,
    GraphQLSchema,
)
from pydantic_ai import capture_run_messages, Agent, ModelSettings, ModelRetry
import requests

from .common import BASE_MODEL, logger
from ..cube import CUBE_API, MODEL_CODE_BLOCKS


def get_schema() -> GraphQLSchema:
    query = get_introspection_query(descriptions=True)
    response = requests.post(f"{CUBE_API}/graphql", json={"query": query})
    return build_client_schema(response.json()["data"])


SCHEMA = get_schema()
INSTRUCTIONS = f"""\
Your role is to generate GraphQL queries to retrieve data from Cube's GraphQL API.
Based on the user's objective, create appropriate GraphQL queries.
The GraphQL schema is as follows:

```
{print_schema(SCHEMA)}
```

Include only the GraphQL query in your response, without any additional explanation.
For example, respond like this:

NOTE: The backticks themselves are not necessary! They are only used here to enclose the Markdown code block for explanation purposes.

```
query {{
  cube {{
    users {{
      count
      gender
    }}
    orders {{
      created_at {{
        day
      }}
    }}
  }}
}}
```

The Cube model definitions are as follows (check the descriptions if necessary):

{"\n".join(MODEL_CODE_BLOCKS)}
"""


graphql_agent = Agent(
    BASE_MODEL,
    model_settings=ModelSettings(),
    instructions=INSTRUCTIONS,
    output_type=str,
)


@graphql_agent.output_validator
def validate_graphql_query(output: str) -> str:
    errs = []
    try:
        errs = validate(SCHEMA, parse(output))
    except Exception as e:
        raise ModelRetry(f"Invalid GraphQL query: {e}")

    if 0 < len(errs):
        raise ModelRetry(f"Invalid GraphQL query: {errs}")

    return output


def run_graphql_agent_with_log(prompt: str):
    with capture_run_messages() as messages:
        try:
            response = graphql_agent.run_sync(prompt)
        except Exception as e:
            for m in messages:
                logger.error(m)
            raise e

        for m in response.all_messages():
            logger.info(m)
        return response
