#!/usr/bin/env python
"""Prepare repository for Render build — data, modeling CSV, optional model."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crimecast.data import model_bundle_dir, resolve_data_paths  # noqa: E402
from crimecast.features import prepare_features_for_sitaka  # noqa: E402


def main() -> None:
    paths = resolve_data_paths(ROOT)

    if not paths["train"].exists() and not paths["train_demo"].exists():
        raise SystemExit(
            "Missing data/train_demo.csv in repository. "
            "Run scripts/create_demo_data.py locally and commit the demo files."
        )

    if not paths["modeling"].exists():
        prepare_features_for_sitaka(output_path=paths["modeling"])
        print(f"Generated {paths['modeling']}")

    bundle = model_bundle_dir()
    if not (bundle / "model.joblib").exists():
        print("No shipped model bundle — training lightweight model during build…")
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "train_shipped_model.py")])

    print("Render bootstrap complete.")


if __name__ == "__main__":
    main()
