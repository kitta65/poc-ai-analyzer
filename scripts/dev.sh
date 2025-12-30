#!/usr/bin/env bash
set -euo pipefail
cd $(git rev-parse --show-toplevel)

uv run streamlit run --server.headless true main.py
