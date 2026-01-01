from graphql import (
    build_client_schema,
    get_introspection_query,
    validate,
    parse,
    print_schema,
    GraphQLSchema,
)
from pydantic_ai import Agent, ModelSettings, ModelRetry
import requests

from .common import BASE_MODEL
from ..cube import CUBE_API


def get_schema() -> GraphQLSchema:
    query = get_introspection_query(descriptions=True)
    response = requests.post(f"{ CUBE_API }/graphql", json={"query": query})
    return build_client_schema(response.json()["data"])


def get_meta():
    response = requests.post(f"{ CUBE_API }/v1/meta")
    return response.text


SCHEMA = get_schema()
META = get_meta()
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

Refer to the metadata retrieved from Cube in advance if necessary.
Descriptions may be included.

```
{META}
```
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
