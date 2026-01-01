from pathlib import Path
from typing import Any

import requests

from .logging import logger

CUBE_API = "http://localhost:4000/cubejs-api"

# read cube definitions
MODEL_DIR = Path.cwd() / "cube" / "model" / "cubes"
MODEL_CODE_BLOCKS = []
for file in MODEL_DIR.iterdir():
    if file.suffix == ".yml":
        with open(MODEL_DIR / file, "r") as f:
            MODEL_CODE_BLOCKS.append(f"""\
```
#----- {file.name}-----
{f.read()}
```
""")


def get_data_by_query(query: str) -> list[dict[str, Any]]:
    response = requests.post(f"{CUBE_API}/graphql", json={"query": query})
    data = response.json().get("data")
    # TODO: impl retry logic. https://cube.dev/docs/product/apis-integrations/core-data-apis/rest-api#continue-wait
    if data is None:
        logger.info(f"status_code: {response.status_code}")
        logger.info(f"text: {response.text}")

    return [_flatten_dict(row) for row in data.get("cube")]


def _flatten_dict(outer_dict: dict[str, Any]) -> dict[str, Any]:
    res = {}
    for key, val in outer_dict.items():
        if not isinstance(val, dict):
            res[key] = val
            continue

        inner_dict = _flatten_dict(val)
        for k, v in inner_dict.items():
            res[f"{key}__{k}"] = v

    return res
