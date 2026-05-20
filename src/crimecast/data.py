from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

COMPETITION_SLUG = "crime-cast-forecasting-crime-categories"
TARGET_COLUMN = "Crime_Category"
DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"

# Columns withheld from modeling (identifiers, post-incident workflow fields).
EXCLUDED_FROM_MODELING = {
    "Status",
    "Status_Description",
    "Cross_Street",
    "Location",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_data_paths(root: Path | None = None) -> dict[str, Path]:
    base = root or project_root()
    data_dir = base / "data"
    return {
        "train": data_dir / "train.csv",
        "train_demo": data_dir / "train_demo.csv",
        "test": data_dir / "test.csv",
        "sample": data_dir / "sample.csv",
        "modeling": data_dir / "train_modeling.csv",
    }


def active_train_path() -> Path:
    paths = resolve_data_paths()
    if paths["train"].exists():
        return paths["train"]
    if paths["train_demo"].exists():
        return paths["train_demo"]
    raise FileNotFoundError(
        "No training data found. Expected `data/train.csv` or bundled `data/train_demo.csv`. "
        f"Download from Kaggle: kaggle competitions download -c {COMPETITION_SLUG} -f train.csv -p data"
    )


def load_crimecast_train(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or active_train_path()
    frame = pd.read_csv(csv_path)
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Expected target column '{TARGET_COLUMN}' in {csv_path}")
    return frame


def load_crimecast_test(path: Path | None = None) -> pd.DataFrame:
    paths = resolve_data_paths()
    csv_path = path or paths["test"]
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Test data not found at {csv_path}. "
            f"kaggle competitions download -c {COMPETITION_SLUG} -f test.csv -p data"
        )
    return pd.read_csv(csv_path)


def is_demo_dataset() -> bool:
    paths = resolve_data_paths()
    return not paths["train"].exists() and paths["train_demo"].exists()


def artifacts_dir() -> Path:
    configured = os.environ.get("SITAKA_ARTIFACTS_DIR", "sitaka_artifacts")
    path = Path(configured)
    if not path.is_absolute():
        path = project_root() / path
    return path


def model_bundle_dir() -> Path:
    primary = artifacts_dir() / "models" / "best_model"
    if primary.exists() and (primary / "model.joblib").exists():
        return primary
    shipped = project_root() / "artifacts" / "models" / "best_model"
    if shipped.exists() and (shipped / "model.joblib").exists():
        return shipped
    return primary
