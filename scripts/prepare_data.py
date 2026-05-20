#!/usr/bin/env python
"""Prepare modeling dataset from CrimeCast train.csv."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crimecast.features import prepare_features_for_sitaka  # noqa: E402


def main() -> None:
    output = prepare_features_for_sitaka()
    print(f"Wrote modeling dataset to {output}")


if __name__ == "__main__":
    main()
