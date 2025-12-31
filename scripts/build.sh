#!/bin/bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# ./scripts/build_schema.py
uv run datamodel-codegen \
  --url 'https://vega.github.io/schema/vega-lite/v1.json' \
  --input-file-type jsonschema \
  --output-model pydantic_v2.BaseModel \
  --output app/models/vegalite.py
