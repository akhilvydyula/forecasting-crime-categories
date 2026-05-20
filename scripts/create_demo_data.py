#!/usr/bin/env python
"""Create a committed demo dataset for cloud deployment (Render)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crimecast.data import TARGET_COLUMN, resolve_data_paths  # noqa: E402
from crimecast.features import prepare_features_for_sitaka  # noqa: E402

DEMO_ROWS = 5000
RANDOM_STATE = 42


def main() -> None:
    paths = resolve_data_paths(ROOT)
    source = paths["train"] if paths["train"].exists() else paths["train_demo"]
    if not source.exists():
        raise FileNotFoundError("Need data/train.csv to build demo dataset.")

    frame = pd.read_csv(source)
    if len(frame) > DEMO_ROWS:
        frame = frame.sample(DEMO_ROWS, random_state=RANDOM_STATE).sort_index()

    demo_path = paths["train_demo"]
    frame.to_csv(demo_path, index=False)
    print(f"Wrote {len(frame)} rows to {demo_path}")

    modeling_path = prepare_features_for_sitaka(
        output_path=paths["modeling"],
        raw=frame,
    )
    print(f"Wrote modeling dataset to {modeling_path}")
    print(f"Categories: {frame[TARGET_COLUMN].nunique()}")


if __name__ == "__main__":
    main()
