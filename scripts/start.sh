#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8501}"
export PYTHONPATH="${PYTHONPATH:-src}"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

exec streamlit run app/streamlit_app.py \
  --server.port="${PORT}" \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
