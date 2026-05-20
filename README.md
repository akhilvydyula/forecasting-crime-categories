# CrimeCast CBO Intelligence Console

Enterprise Streamlit application for advanced operational-risk analysis on the [CrimeCast: Forecasting Crime Categories](https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories) Kaggle competition, powered by **[SITAKA API](https://pypi.org/project/sitaka-api/)** for AutoML training, EDA, MLflow tracking, and model governance.

Built for **Chief Business Officer (CBO)** and enterprise risk forums at large banking institutions—translating municipal crime incident patterns into geographic, temporal, and predictive intelligence for physical security and fraud-adjacent planning.

## Features

| Capability | Description |
| --- | --- |
| Executive dashboard | KPI cards, category mix, committee briefing notes |
| Geographic intelligence | Mapbox incident map, composite area risk ranking |
| Temporal analytics | Monthly volume trends, hour-of-day patterns, premise concentration |
| SITAKA Model Lab | Profile → AutoML train → evaluate → deploy scaffold |
| Scenario simulator | What-if crime category scoring from the latest model bundle |
| Documentation | Embedded CBO guide, architecture, and deployment playbooks |

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Kaggle credentials required: https://www.kaggle.com/docs/api
kaggle competitions download -c crime-cast-forecasting-crime-categories -f train.csv -p data
python scripts/prepare_data.py

streamlit run app/streamlit_app.py
```

### Deploy to Render

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md#render-deployment) or use the included `render.yaml` Blueprint.

Optional full SITAKA CLI pipeline:

```powershell
sitaka run --config config/sitaka.yaml
```

## Project structure

```text
app/streamlit_app.py          # CBO multi-page console
src/crimecast/                # Data, features, analytics, SITAKA bridge
config/sitaka.yaml            # AutoML + MLflow configuration
scripts/prepare_data.py       # Build train_modeling.csv
docs/                         # CBO_EXECUTIVE_GUIDE, ARCHITECTURE, DEPLOYMENT
data/                         # Kaggle CSVs (train/test gitignored)
```

## Documentation

- [CBO Executive Guide](docs/CBO_EXECUTIVE_GUIDE.md) — how risk leaders use each page
- [Architecture](docs/ARCHITECTURE.md) — components, data flow, SITAKA modes
- [Deployment](docs/DEPLOYMENT.md) — local, Docker, enterprise hardening

## Competition data

| File | Rows (approx.) | Role |
| --- | --- | --- |
| `train.csv` | 20,000 | Labeled incidents with `Crime_Category` target |
| `test.csv` | — | Submission features (ID only in sample) |
| `sample.csv` | 5 | Submission format example |

Target column: **`Crime_Category`**

## SITAKA API

This project uses [sitaka-api](https://pypi.org/project/sitaka-api/) for:

- Exploratory data analysis reports
- Optuna-driven AutoML (Random Forest, Extra Trees, Gradient Boosting, Linear)
- MLflow experiment logging (`./mlruns`)
- Portable `model.joblib` bundles for the Scenario Simulator

Install: `pip install sitaka-api[deploy,parquet]`

## License

MIT (application code). Kaggle competition data subject to [competition rules](https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories/rules).

## Author

Veliation AI — operational-risk analytics on public safety data for enterprise demonstrations.
