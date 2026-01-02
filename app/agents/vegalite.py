from typing import Literal
import pandas as pd
from pydantic import BaseModel
from pydantic_ai import capture_run_messages, Agent, ModelSettings, RunContext

from .common import BASE_MODEL, logger


class MarkSchema(BaseModel):
    type: Literal["circle", "bar", "line"]


class FieldSchema(BaseModel):
    field: str
    type: Literal["quantitative", "temporal", "ordinal", "nominal"]
    # https://vega.github.io/vega-lite/docs/aggregate.html#ops
    aggregate: Literal["sum", "average", "min", "max", "count"] | None = None


class EncodingSchema(BaseModel):
    x: FieldSchema
    y: FieldSchema
    color: FieldSchema | None = None


class VegaLiteSchema(BaseModel):
    mark: MarkSchema
    encoding: EncodingSchema


INSTRUCTIONS = """\
You are an excellent data visualization assistant.
Generate JSON in Vega-Lite format based on the user's request.
"""


vegalite_agent = Agent(
    BASE_MODEL,
    model_settings=ModelSettings(),
    instructions=INSTRUCTIONS,
    output_type=VegaLiteSchema,
    deps_type=pd.DataFrame,
)


@vegalite_agent.instructions
def add_dataframe_schema(ctx: RunContext[pd.DataFrame]) -> str:
    return f"""\
The data columns and types are as follows.
Internally prepared as a pandas DataFrame.

```
{ctx.deps.dtypes.astype(str).to_dict()}
```

This is the first few rows of the data.

```
{ctx.deps.head()}
```
"""


def run_vegalite_agent_with_log(prompt: str, df: pd.DataFrame):
    with capture_run_messages() as messages:
        try:
            response = vegalite_agent.run_sync(prompt, deps=df)
        except Exception as e:
            for m in messages:
                logger.error(m)
            raise e

        for m in response.all_messages():
            logger.info(m)
        return response
