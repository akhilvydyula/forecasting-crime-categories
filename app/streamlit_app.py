"""
CrimeCast CBO Intelligence Console — enterprise Streamlit application.

Competition: https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories
ML platform: https://pypi.org/project/sitaka-api/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crimecast.analytics import (  # noqa: E402
    area_risk_table,
    category_mix,
    compute_executive_kpis,
    temporal_profile,
)
from crimecast.data import (  # noqa: E402
    TARGET_COLUMN,
    is_demo_dataset,
    load_crimecast_train,
    model_bundle_dir,
    resolve_data_paths,
)
from crimecast.features import build_modeling_frame, prepare_features_for_sitaka  # noqa: E402
from crimecast.sitaka_bridge import (  # noqa: E402
    default_config_path,
    ensure_modeling_dataset,
    load_or_create_config,
    remote_health,
    run_local_deploy,
    run_local_evaluate,
    run_local_predict,
    run_local_profile,
    run_local_train,
)
from sitaka_api.bundle import load_model_bundle  # noqa: E402

COMPETITION_URL = "https://www.kaggle.com/competitions/crime-cast-forecasting-crime-categories"
SITAKA_URL = "https://pypi.org/project/sitaka-api/"


@st.cache_data(show_spinner="Loading CrimeCast training data…")
def cached_train() -> pd.DataFrame:
    return load_crimecast_train()


def ensure_data_loaded() -> pd.DataFrame | None:
    try:
        return cached_train()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.info(
            "For local development, run:\n\n"
            "`kaggle competitions download -c crime-cast-forecasting-crime-categories -f train.csv -p data`"
        )
        return None


@st.cache_data
def cached_modeling() -> pd.DataFrame:
    path = ensure_modeling_dataset()
    return pd.read_csv(path)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; max-width: 1200px; }
        .metric-card {
            background: linear-gradient(135deg, #0B3D91 0%, #1E5AA8 100%);
            color: white; padding: 1rem 1.2rem; border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        .metric-card h3 { margin: 0; font-size: 1.6rem; }
        .metric-card p { margin: 0.2rem 0 0; opacity: 0.9; font-size: 0.85rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(kpis) -> None:
    cols = st.columns(4)
    cards = [
        ("Total incidents", f"{kpis.total_incidents:,}", "Lending & branch footprint exposure"),
        ("Dominant category", kpis.top_category, f"{kpis.top_category_share:.1%} of portfolio mix"),
        ("Violent crime share", f"{kpis.violent_crime_share:.1%}", "Physical security escalation"),
        ("Fraud / white-collar", f"{kpis.fraud_share:.1%}", "Financial crime & AML adjacency"),
    ]
    for col, (title, value, subtitle) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><p>{title}</p>'
                f"<h3>{value}</h3><p>{subtitle}</p></div>",
                unsafe_allow_html=True,
            )


def page_executive() -> None:
    st.title("Executive Overview")
    st.caption(
        "Chief Business Officer view — category mix, reporting latency, and weapon involvement "
        "for operational risk committees."
    )
    frame = ensure_data_loaded()
    if frame is None:
        return
    if is_demo_dataset():
        st.info("Showing bundled demo dataset (5,000 incidents). Upload full `train.csv` locally for 20k rows.")
    kpis = compute_executive_kpis(frame)
    render_kpi_cards(kpis)

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        mix = category_mix(frame)
        fig = px.bar(
            mix,
            x="share",
            y="category",
            orientation="h",
            title="Crime category mix",
            color="category",
        )
        fig.update_layout(showlegend=False, height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        st.subheader("Committee briefing notes")
        st.markdown(
            f"""
            - **Coverage:** {kpis.distinct_areas} police reporting areas represented in the training set.
            - **Reporting lag:** average **{kpis.avg_report_lag_days:.1f} days** between occurrence and report.
            - **Weapon involvement:** **{kpis.weapon_involved_rate:.1%}** of incidents reference a weapon code.
            - **Modeling target:** `{TARGET_COLUMN}` with **{kpis.category_count}** classes.

            Use this view in quarterly risk forums to align physical security spend with observed
            category concentration. Pair with the **Model Lab** page for AutoML forecasts powered by
            [SITAKA API]({SITAKA_URL}).
            """
        )


def page_geographic() -> None:
    st.title("Geographic Intelligence")
    st.caption("Map incident density and rank areas by composite violent + fraud risk.")
    frame = ensure_data_loaded()
    if frame is None:
        return
    map_df = frame.dropna(subset=["Latitude", "Longitude"]).copy()
    map_df["size"] = 4
    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        color=TARGET_COLUMN,
        hover_name="Area_Name",
        hover_data=["Premise_Description", "Part 1-2"],
        zoom=9,
        height=520,
        title="Incident geospatial distribution",
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    risk = area_risk_table(frame)
    display = risk.copy()
    display["violent_rate"] = display["violent_rate"].map(lambda v: f"{v:.1%}")
    display["fraud_rate"] = display["fraud_rate"].map(lambda v: f"{v:.1%}")
    display["risk_score"] = display["risk_score"].map(lambda v: f"{v:.3f}")
    display["avg_victim_age"] = display["avg_victim_age"].map(lambda v: f"{v:.1f}")
    st.subheader("Area risk ranking (composite score)")
    st.dataframe(display, use_container_width=True, hide_index=True)


def page_temporal() -> None:
    st.title("Temporal & Operational Patterns")
    frame = ensure_data_loaded()
    if frame is None:
        return
    profile = temporal_profile(frame)
    fig = px.area(
        profile,
        x="month",
        y="incidents",
        color=TARGET_COLUMN,
        title="Monthly incident volume by category",
    )
    fig.update_layout(height=440, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    hour_df = build_modeling_frame(frame)
    if "occurred_hour" in hour_df.columns:
        hour_counts = (
            hour_df.groupby(["occurred_hour", TARGET_COLUMN])
            .size()
            .reset_index(name="incidents")
            .dropna(subset=["occurred_hour"])
        )
        fig_hour = px.line(
            hour_counts,
            x="occurred_hour",
            y="incidents",
            color=TARGET_COLUMN,
            markers=True,
            title="Incidents by hour of day (occurrence time)",
        )
        st.plotly_chart(fig_hour, use_container_width=True)

    st.subheader("Premise concentration")
    premise = (
        frame["Premise_Description"]
        .value_counts()
        .head(12)
        .rename_axis("premise")
        .reset_index(name="incidents")
    )
    st.plotly_chart(
        px.bar(premise, x="incidents", y="premise", orientation="h", title="Top premises"),
        use_container_width=True,
    )


def page_model_lab() -> None:
    st.title("Model Lab — SITAKA AutoML")
    st.markdown(
        f"""
        Train and govern crime-category classifiers with **[sitaka-api]({SITAKA_URL})**
        (local workflow services or remote product API). Configuration:
        `{default_config_path()}`.
        """
    )

    mode = st.radio(
        "Execution mode",
        ["Local workflow (recommended)", "Remote SITAKA API"],
        horizontal=True,
    )

    if mode.startswith("Remote"):
        api_url = st.text_input("SITAKA API URL", value="http://127.0.0.1:8000")
        st.caption("Set `SITAKA_API_URL` and optional `SITAKA_API_KEY` in the environment.")
        if st.button("Check API health"):
            import os

            os.environ["SITAKA_API_URL"] = api_url
            try:
                payload = remote_health()
                st.success(f"API healthy: {payload}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not reach API: {exc}")
                st.info("Start the server with: `sitaka server` or `python -m sitaka_api server`")
        st.stop()

    col1, col2, col3 = st.columns(3)
    with col1:
        run_profile = st.button("1. Profile data (EDA)")
    with col2:
        run_train = st.button("2. Train AutoML")
    with col3:
        run_eval = st.button("3. Evaluate bundle")

    config = load_or_create_config()

    if run_profile:
        with st.spinner("Generating SITAKA EDA report…"):
            report_path = run_local_profile(config)
        st.success(f"EDA report written to `{report_path}`")
        st.markdown(report_path.read_text(encoding="utf-8"))

    if run_train:
        trials = st.session_state.get("n_trials", config.automl.n_trials)
        config.automl.n_trials = min(trials, 8)
        config.automl.max_rows = min(config.automl.max_rows or 15000, 8000)
        with st.spinner(f"Running Optuna search ({config.automl.n_trials} trials)…"):
            summary = run_local_train(config)
        st.session_state["last_train"] = summary
        st.success("Training complete.")
        st.json(summary.metrics)

    if run_eval:
        with st.spinner("Evaluating held-out split…"):
            metrics = run_local_evaluate(config)
        st.metric("Hold-out metrics", json.dumps(metrics))

    bundle_dir = model_bundle_dir()
    if bundle_dir.exists() and (bundle_dir / "model.joblib").exists():
        _, metadata = load_model_bundle(bundle_dir)
        st.subheader("Registered model metadata")
        st.json(
            {
                "model_name": metadata.model_name,
                "metric_name": metadata.metric_name,
                "metric_value": metadata.metric_value,
                "features": metadata.features,
            }
        )
        if st.button("Generate Streamlit deployment scaffold"):
            out = run_local_deploy(config, framework="streamlit")
            st.info(f"Deployment artifacts: `{out}`")

    with st.expander("Advanced training controls"):
        config.automl.n_trials = st.slider("Optuna trials", 3, 40, config.automl.n_trials)
        config.automl.max_rows = st.number_input(
            "Max training rows",
            min_value=1000,
            max_value=20000,
            value=config.automl.max_rows or 15000,
            step=500,
        )
        st.session_state["n_trials"] = config.automl.n_trials


SCENARIO_DRIVERS = [
    "Latitude",
    "Longitude",
    "Area_Name",
    "Part 1-2",
    "Victim_Age",
    "Victim_Sex",
    "premise_group",
    "report_lag_bucket",
    "occurred_hour",
    "occurred_day_of_week",
    "has_weapon",
]


def page_scenario() -> None:
    st.title("Scenario Simulator")
    st.caption("Score a synthetic incident profile against the latest SITAKA model bundle.")
    modeling = cached_modeling()
    feature_cols = [c for c in modeling.columns if c != TARGET_COLUMN]

    defaults = modeling[feature_cols].median(numeric_only=True)
    modes = modeling[feature_cols].mode().iloc[0].to_dict()
    record: dict = {}
    for col in feature_cols:
        series = modeling[col]
        if pd.api.types.is_numeric_dtype(series):
            record[col] = float(defaults.get(col, series.median()))
        else:
            record[col] = str(modes.get(col, series.dropna().astype(str).iloc[0]))

    st.subheader("Key incident drivers")
    cols = st.columns(3)
    drivers = [c for c in SCENARIO_DRIVERS if c in feature_cols]
    for idx, column in enumerate(drivers):
        with cols[idx % 3]:
            series = modeling[column]
            if pd.api.types.is_numeric_dtype(series):
                value = float(defaults.get(column, 0))
                record[column] = st.number_input(column, value=value)
            else:
                options = sorted(series.dropna().astype(str).unique().tolist())[:80]
                default = str(modes.get(column, options[0] if options else ""))
                record[column] = st.selectbox(
                    column,
                    options=options,
                    index=options.index(default) if default in options else 0,
                )
    st.caption("Remaining features are filled with cohort medians/modes for scoring.")

    if st.button("Predict crime category", type="primary"):
        try:
            predictions = run_local_predict([record])
            st.success(f"Predicted category: **{predictions[0]}**")
        except FileNotFoundError as exc:
            st.warning(str(exc))
        except Exception as exc:  # noqa: BLE001
            st.error(f"Prediction failed: {exc}")


def page_docs() -> None:
    st.title("Documentation & Governance")
    docs_dir = ROOT / "docs"
    for doc_name in ("CBO_EXECUTIVE_GUIDE.md", "ARCHITECTURE.md", "DEPLOYMENT.md"):
        path = docs_dir / doc_name
        if path.exists():
            st.subheader(doc_name.replace("_", " ").replace(".md", ""))
            st.markdown(path.read_text(encoding="utf-8"))
        else:
            st.warning(f"Missing {path}")

    st.subheader("Data acquisition")
    st.code(
        "kaggle competitions download -c crime-cast-forecasting-crime-categories -f train.csv -p data\n"
        "python scripts/prepare_data.py",
        language="bash",
    )
    paths = resolve_data_paths()
    status = {name: path.exists() for name, path in paths.items()}
    st.json(status)


def main() -> None:
    st.set_page_config(
        page_title="CrimeCast CBO Intelligence",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()

    st.sidebar.image(
        "https://img.icons8.com/fluency/96/bank-building.png",
        width=72,
    )
    st.sidebar.title("CrimeCast Console")
    st.sidebar.caption("Enterprise operational-risk analytics")
    st.sidebar.markdown(
        f"[Kaggle competition]({COMPETITION_URL}) · [SITAKA API]({SITAKA_URL})"
    )

    pages = {
        "Executive Overview": page_executive,
        "Geographic Intelligence": page_geographic,
        "Temporal Patterns": page_temporal,
        "Model Lab (SITAKA)": page_model_lab,
        "Scenario Simulator": page_scenario,
        "Documentation": page_docs,
    }
    selection = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[selection]()


if __name__ == "__main__":
    main()
