# CrimeCast CBO Intelligence Console

[![License: MIT](https://img.shields.io/github/license/akhilvydyula/forecasting-crime-categories)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories)
[![GitHub stars](https://img.shields.io/github/stars/akhilvydyula/forecasting-crime-categories?style=social)](https://github.com/akhilvydyula/forecasting-crime-categories/stargazers)
[![Open Source](https://img.shields.io/badge/open%20source-welcome-brightgreen)](#open-source)

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

## Open source

This repository is **open source** under the [MIT License](LICENSE). Stars, issues, and pull requests are welcome — they help others discover the project and improve it for the community.

### How you can help

- **Star** the repo if you find it useful — it helps visibility on GitHub Explore and search.
- **Open an issue** for bugs, ideas, or questions.
- **Submit a pull request** with a focused change and a clear description.
- **Share** the project with data scientists working on public-safety or risk analytics.

Maintained by [Akhil Vydyula](https://github.com/akhilvydyula) as part of the Skills Marathon ML portfolio.

## License

Application code is released under the [MIT License](LICENSE). Kaggle competition data is subject to [competition rules](https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories/rules).
