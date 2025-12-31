#!/usr/bin/env -S uv run --script
import os
from pathlib import Path
import requests
from graphql import build_client_schema, get_introspection_query, print_schema

ROOT_DIR = Path(__file__).parents[1]
os.chdir(ROOT_DIR)

# see also https://github.com/graphql-python/graphql-core/blob/main/docs/usage/introspection.rst

query = get_introspection_query(descriptions=True)
response = requests.post(
    "http://localhost:4000/cubejs-api/graphql", json={"query": query}
)
schema = build_client_schema(response.json()["data"])
sdl = print_schema(schema)

with open(ROOT_DIR / "generated" / "schema.graphql", "w") as f:
    f.write(sdl)
