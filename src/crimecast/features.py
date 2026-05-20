from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from crimecast.data import EXCLUDED_FROM_MODELING, TARGET_COLUMN, load_crimecast_train, resolve_data_paths


def _parse_occurred_hour(time_value: float | int | str | None) -> float | np.nan:
    if pd.isna(time_value):
        return np.nan
    try:
        digits = str(int(float(time_value))).zfill(4)
        hour = int(digits[:2])
        if 0 <= hour <= 23:
            return float(hour)
    except (TypeError, ValueError):
        pass
    return np.nan


def _top_category_bucket(series: pd.Series, top_n: int = 20, label: str = "Other") -> pd.Series:
    filled = series.fillna(label).astype(str)
    keep = filled.value_counts().head(top_n).index
    return filled.where(filled.isin(keep), other=label)


def _report_lag_bucket(days: pd.Series) -> pd.Series:
    bins = [-1, 0, 3, 7, 30, 10_000]
    labels = ["same_day", "1_3_days", "4_7_days", "8_30_days", "30_plus_days"]
    return pd.cut(days.fillna(0), bins=bins, labels=labels).astype(str)


def build_modeling_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Engineer features suitable for AutoML and executive analytics."""
    frame = raw.copy()
    frame["Date_Occurred"] = pd.to_datetime(
        frame["Date_Occurred"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce"
    )
    frame["Date_Reported"] = pd.to_datetime(
        frame["Date_Reported"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce"
    )
    frame["occurred_year"] = frame["Date_Occurred"].dt.year
    frame["occurred_month"] = frame["Date_Occurred"].dt.month
    frame["occurred_day_of_week"] = frame["Date_Occurred"].dt.dayofweek
    frame["occurred_hour"] = frame["Time_Occurred"].map(_parse_occurred_hour)
    report_lag = (frame["Date_Reported"] - frame["Date_Occurred"]).dt.days
    frame["report_lag_bucket"] = _report_lag_bucket(report_lag)
    frame["has_weapon"] = frame["Weapon_Used_Code"].notna().astype(int)
    frame["victim_age_missing"] = frame["Victim_Age"].isna().astype(int)
    frame["Victim_Age"] = frame["Victim_Age"].fillna(frame["Victim_Age"].median()).clip(0, 100)
    frame["Latitude"] = frame["Latitude"].round(2)
    frame["Longitude"] = frame["Longitude"].round(2)
    if "Premise_Description" in frame.columns:
        frame["premise_group"] = _top_category_bucket(frame["Premise_Description"])

    drop_columns = {
        "Date_Occurred",
        "Date_Reported",
        "Time_Occurred",
        "Modus_Operandi",
        "Weapon_Description",
        "Weapon_Used_Code",
        "Reporting_District_no",
        "Premise_Code",
        "Premise_Description",
        *EXCLUDED_FROM_MODELING,
    }
    modeling = frame.drop(columns=[c for c in drop_columns if c in frame.columns])

    for column in modeling.select_dtypes(include="object").columns:
        modeling[column] = modeling[column].fillna("UNKNOWN").astype(str)
    for column in modeling.select_dtypes(include="number").columns:
        modeling[column] = modeling[column].fillna(modeling[column].median())

    return modeling


def prepare_features_for_sitaka(
    output_path: Path | None = None,
    raw: pd.DataFrame | None = None,
) -> Path:
    """Persist a modeling-ready CSV for SITAKA AutoML."""
    paths = resolve_data_paths()
    destination = output_path or paths["modeling"]
    source = raw if raw is not None else load_crimecast_train()
    modeling = build_modeling_frame(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    modeling.to_csv(destination, index=False)
    return destination
