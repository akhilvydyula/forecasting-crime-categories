# CrimeCast CBO Executive Guide

## Purpose

This application supports **Chief Business Officer (CBO)** and operational-risk leadership teams at large banking enterprises. It connects public-safety incident intelligence from the [CrimeCast Kaggle competition](https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories) to actionable views on:

- Category concentration (property, violent, fraud, public-order)
- Geographic exposure near branch and ATM footprints
- Temporal patterns for staffing and third-party guard contracts
- Governed machine-learning forecasts via [SITAKA API](https://pypi.org/project/sitaka-api/)

> **Disclaimer:** CrimeCast data describes municipal police incidents. Map overlays are for **risk analytics demonstrations** only. Production branch-risk models must use bank-controlled data, legal review, and model-risk management (MRM) sign-off.

## Competition objective

Predict `Crime_Category` from incident attributes (location, timing, victim demographics, premise, weapons, reporting metadata). Categories include:

| Category | Business lens |
| --- | --- |
| Property Crimes | Physical asset / premises loss |
| Violent Crimes | Staff and customer safety escalation |
| Fraud and White-Collar Crimes | Financial crime adjacency, AML monitoring |
| Crimes against Public Order | Reputational and community disruption |
| Crimes against Persons | Direct harm scenarios |
| Other Crimes | Residual / heterogeneous bucket |

## Console pages

### 1. Executive Overview

Use in **quarterly risk committee** readouts. KPI cards summarize volume, dominant category, violent share, and fraud share. The horizontal bar chart shows portfolio mix—useful when reallocating security OPEX across regions.

### 2. Geographic Intelligence

Scatter map of `Latitude` / `Longitude` colored by category. The **area risk table** ranks police reporting areas with a composite score weighting violent rate, fraud rate, and incident volume. Overlay results with internal branch density layers in your GIS toolchain.

### 3. Temporal Patterns

Monthly area chart by category and hourly line chart derived from `Time_Occurred`. Supports decisions on extended hours, cash-handling windows, and vendor guard schedules.

### 4. Model Lab (SITAKA)

Runs the SITAKA workflow locally:

1. **Profile** — writes `sitaka_artifacts/reports/crimecast_eda.md`
2. **Train** — Optuna AutoML over sklearn pipelines; registers `model.joblib`
3. **Evaluate** — hold-out accuracy / macro-F1
4. **Deploy** — optional generated Streamlit/FastAPI service scaffold

MLflow experiments are stored under `./mlruns` when enabled in `config/sitaka.yaml`.

### 5. Scenario Simulator

What-if scoring for a synthetic incident. Key drivers are exposed in the UI; remaining features default to cohort statistics so executives can test “what if violent crime rises in Area X?” without editing YAML.

### 6. Documentation

Embedded governance and deployment references (this guide, architecture, deployment).

## Recommended forum narrative

1. **Context** — CrimeCast provides 20k labeled incidents for category forecasting practice.
2. **Exposure** — Show geographic and temporal pages tied to markets where the bank operates.
3. **Decision** — Highlight category mix shifts quarter-over-quarter.
4. **Science** — Present SITAKA model metrics and EDA leakage hints.
5. **Action** — Translate top risk areas into security projects with owners and dates.

## Data governance notes

- **Excluded from modeling:** `Status`, `Status_Description`, `Location`, `Cross_Street` (workflow or high-cardinality text).
- **Target:** `Crime_Category`
- **Acquisition:** Kaggle CLI (`train.csv`, `test.csv`); see root README.

## Contacts & references

- Competition: https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories
- SITAKA package: https://pypi.org/project/sitaka-api/
- Source repository: GitLab `veliation-ai/forecasting-crime-categories`
