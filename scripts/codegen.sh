#!/bin/bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

uv run datamodel-codegen \
  --url 'https://vega.github.io/schema/vega-lite/v6.json' \
  --input-file-type jsonschema \
  --output-model pydantic_v2.BaseModel \
  --output app/agents/vegalite_schema.py
