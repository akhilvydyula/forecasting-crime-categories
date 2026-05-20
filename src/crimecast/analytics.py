from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from crimecast.data import TARGET_COLUMN


@dataclass(frozen=True)
class ExecutiveKpis:
    total_incidents: int
    category_count: int
    top_category: str
    top_category_share: float
    property_crime_share: float
    violent_crime_share: float
    fraud_share: float
    avg_report_lag_days: float
    weapon_involved_rate: float
    distinct_areas: int


def compute_executive_kpis(frame: pd.DataFrame) -> ExecutiveKpis:
    counts = frame[TARGET_COLUMN].value_counts(normalize=True)
    top_category = str(counts.index[0])
    top_share = float(counts.iloc[0])

    def share(label: str) -> float:
        return float((frame[TARGET_COLUMN] == label).mean())

    report_lag = np.nan
    if {"Date_Reported", "Date_Occurred"}.issubset(frame.columns):
        reported = pd.to_datetime(frame["Date_Reported"], errors="coerce")
        occurred = pd.to_datetime(frame["Date_Occurred"], errors="coerce")
        report_lag = float((reported - occurred).dt.days.mean())

    weapon_rate = float(frame["Weapon_Used_Code"].notna().mean()) if "Weapon_Used_Code" in frame else 0.0
    areas = int(frame["Area_Name"].nunique()) if "Area_Name" in frame else 0

    return ExecutiveKpis(
        total_incidents=len(frame),
        category_count=int(frame[TARGET_COLUMN].nunique()),
        top_category=top_category,
        top_category_share=top_share,
        property_crime_share=share("Property Crimes"),
        violent_crime_share=share("Violent Crimes"),
        fraud_share=share("Fraud and White-Collar Crimes"),
        avg_report_lag_days=report_lag if not np.isnan(report_lag) else 0.0,
        weapon_involved_rate=weapon_rate,
        distinct_areas=areas,
    )


def category_mix(frame: pd.DataFrame) -> pd.DataFrame:
    mix = (
        frame[TARGET_COLUMN]
        .value_counts()
        .rename_axis("category")
        .reset_index(name="incidents")
    )
    mix["share"] = mix["incidents"] / mix["incidents"].sum()
    return mix


def area_risk_table(frame: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    grouped = (
        frame.groupby("Area_Name", dropna=False)
        .agg(
            incidents=("Area_Name", "size"),
            violent_rate=(TARGET_COLUMN, lambda s: (s == "Violent Crimes").mean()),
            fraud_rate=(TARGET_COLUMN, lambda s: (s == "Fraud and White-Collar Crimes").mean()),
            avg_victim_age=("Victim_Age", "mean"),
        )
        .reset_index()
    )
    grouped["risk_score"] = (
        0.5 * grouped["violent_rate"]
        + 0.35 * grouped["fraud_rate"]
        + 0.15 * (grouped["incidents"] / grouped["incidents"].max())
    )
    return grouped.sort_values("risk_score", ascending=False).head(top_n)


def temporal_profile(frame: pd.DataFrame) -> pd.DataFrame:
    working = frame.copy()
    working["Date_Occurred"] = pd.to_datetime(working["Date_Occurred"], errors="coerce")
    working["month"] = working["Date_Occurred"].dt.to_period("M").astype(str)
    profile = (
        working.groupby(["month", TARGET_COLUMN], dropna=False)
        .size()
        .reset_index(name="incidents")
    )
    return profile
