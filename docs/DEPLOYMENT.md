# Deployment Guide

## Prerequisites

- Python **3.10+**
- [Kaggle API credentials](https://www.kaggle.com/docs/api) configured (`~/.kaggle/kaggle.json`)
- 4 GB RAM minimum for AutoML on 15k rows

## Local development

```powershell
cd forecasting-crime-categories
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Download competition data
kaggle competitions download -c crime-cast-forecasting-crime-categories -f train.csv -p data
kaggle competitions download -c crime-cast-forecasting-crime-categories -f test.csv -p data

# Feature engineering for SITAKA
python scripts/prepare_data.py

# Optional: full SITAKA pipeline from CLI
sitaka run --config config/sitaka.yaml

# Launch CBO console
streamlit run app/streamlit_app.py
```

Open http://localhost:8501

## Environment variables

| Variable | Purpose |
| --- | --- |
| `SITAKA_API_URL` | Remote product API base URL (Model Lab remote mode) |
| `SITAKA_API_KEY` | `X-API-Key` header for secured SITAKA deployments |

## Render deployment

This repo includes a [Render Blueprint](https://render.com/docs/blueprint-spec) (`render.yaml`).

### One-click deploy

1. Push the repository to GitHub/GitLab (include committed `data/train_demo.csv` and `artifacts/models/best_model/`).
2. In [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint** → connect the repo.
3. Render runs:
   - `pip install -r requirements.txt`
   - `python scripts/bootstrap_render.py`
   - `bash scripts/start.sh` (binds Streamlit to `$PORT`)

### Manual web service settings

| Setting | Value |
| --- | --- |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt && python scripts/bootstrap_render.py` |
| **Start Command** | `bash scripts/start.sh` |
| **Environment** | `PYTHONPATH=src`, `SITAKA_ARTIFACTS_DIR=artifacts`, `MLFLOW_ENABLED=false` |

### Bundled demo data

Cloud deploys use `data/train_demo.csv` (5,000 stratified rows) when the full Kaggle `train.csv` is not present. For local development with all 20k rows, download via Kaggle CLI.

Regenerate demo + shipped model after feature changes:

```powershell
python scripts/create_demo_data.py
python scripts/train_shipped_model.py
git add data/train_demo.csv artifacts/models/best_model/
```

### Troubleshooting (Render)

| Issue | Resolution |
| --- | --- |
| Build timeout during training | Ensure `artifacts/models/best_model/` is committed; bootstrap skips training when present |
| `No training data found` | Commit `data/train_demo.csv` |
| sklearn unpickle warnings | Keep `scikit-learn==1.7.2` pinned in `requirements.txt` |
| App not reachable | Confirm start command uses `--server.address=0.0.0.0` and `$PORT` |

## Docker (Streamlit only)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install -e . 2>/dev/null || true
ENV PYTHONPATH=/app/src
EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Mount `./data` and `./sitaka_artifacts` as volumes for persistence.

## Enterprise hardening checklist

- [ ] TLS termination at load balancer
- [ ] SSO / RBAC on Streamlit ingress
- [ ] Secrets from vault (not `.env` in images)
- [ ] Read-only container filesystem except `/data` and `/sitaka_artifacts`
- [ ] Central logging (JSON) shipped to SIEM
- [ ] MLflow tracking URI pointed at managed server
- [ ] Model approval workflow before production scoring

## SITAKA server co-deployment

For teams standardizing on the product API:

```powershell
pip install sitaka-api
$env:SITAKA_API_KEY = "rotate-me"
sitaka server --host 0.0.0.0 --port 8000
```

Point the Streamlit **Model Lab** to `http://<host>:8000` or call the SDK from scheduled retraining jobs.

Generated deployment scaffolds (FastAPI / Streamlit / Flask) land in `sitaka_deployment/` after training—see [SITAKA deployment docs](https://pypi.org/project/sitaka-api/).

## CI smoke test

```powershell
python scripts/prepare_data.py
python -c "from crimecast.sitaka_bridge import run_local_profile; print(run_local_profile())"
```

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| `Training data not found` | Run Kaggle download for `train.csv` into `data/` |
| `No trained model bundle` | Complete **Train AutoML** in Model Lab or `sitaka train` |
| Optuna slow on laptop | Lower `automl.n_trials` or `max_rows` in `config/sitaka.yaml` |
| `sitaka` command missing | Use `python -m sitaka_api server` |
