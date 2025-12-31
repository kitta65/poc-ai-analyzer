import pandas as pd
from pydantic_ai import Agent, ModelSettings, RunContext

from .common import BASE_MODEL
from ..models.vegalite import VegaLiteSchema


INSTRUCTIONS = f"""\
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


@vegalite_agent.system_prompt
def add_dataframe_schema(ctx: RunContext[pd.DataFrame]) -> str:
    return f"""\
The data columns and types are as follows.
Internally prepared as a pandas DataFrame.

```
{ctx.deps.dtypes.astype(str).to_dict()}
```
"""
