from __future__ import annotations

from pathlib import Path

import pandas as pd

COMPETITION_SLUG = "crime-cast-forecasting-crime-categories"
TARGET_COLUMN = "Crime_Category"

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
        "test": data_dir / "test.csv",
        "sample": data_dir / "sample.csv",
        "modeling": data_dir / "train_modeling.csv",
    }


def load_crimecast_train(path: Path | None = None) -> pd.DataFrame:
    paths = resolve_data_paths()
    csv_path = path or paths["train"]
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Training data not found at {csv_path}. "
            "Download from Kaggle: "
            f"kaggle competitions download -c {COMPETITION_SLUG} -f train.csv -p data"
        )
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
