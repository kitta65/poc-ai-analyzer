#!/usr/bin/env bash
set -euo pipefail
cd $(git rev-parse --show-toplevel)

cube_container_name="cube-dev-container"
docker container run \
  -d \
  --rm \
  --name $cube_container_name \
  -e CUBEJS_DB_TYPE=bigquery \
  -e CUBEJS_DEV_MODE=true \
  -e CUBEJS_DB_BQ_PROJECT_ID=$(gcloud config get-value project) \
  -e CUBEJS_DB_BQ_CREDENTIALS=$(cat "${HOME}/.config/gcloud/application_default_credentials.json" | base64 | tr -d '\n') \
  -p 4000:4000 \
  -p 15432:15432 \
  -v ./cube:/cube/conf \
  cubejs/cube:v1.3.54
uv run streamlit run --server.headless true main.py
