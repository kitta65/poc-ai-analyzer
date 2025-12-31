from pydantic_ai import Agent, ModelSettings

from .common import BASE_MODEL
from ..models.vegalite import ExtendedUnitSpec as VegaLiteModel


INSTRUCTIONS = f"""\
You are an excellent data visualization assistant.
Please generate visualization specifications following the Vega-Lite specification based on user requests.
Please pay attention to the following points:

- Output must be in JSON format.
- If data processing or preprocessing is required, use Vega-Lite's transform feature.
- The output JSON must comply with the Vega-Lite specification.
- No additional explanations are needed. Output only JSON.
"""


vegalite_agent = Agent(
    BASE_MODEL,
    model_settings=ModelSettings(),
    instructions=INSTRUCTIONS,
    output_type=VegaLiteModel,
)
