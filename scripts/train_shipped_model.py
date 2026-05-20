#!/usr/bin/env python
"""Train a lightweight model bundle committed for Render deployment."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sitaka_api.config import AutoMLConfig, MLflowConfig  # noqa: E402

from crimecast.features import prepare_features_for_sitaka  # noqa: E402
from crimecast.sitaka_bridge import load_or_create_config, run_local_train  # noqa: E402


def main() -> None:
    prepare_features_for_sitaka()
    config = load_or_create_config()
    config = config.model_copy(
        update={
            "artifacts_dir": str(ROOT / "artifacts"),
            "automl": AutoMLConfig(
                enabled_models=["random_forest", "linear"],
                n_trials=4,
                cv_folds=3,
                max_rows=5000,
            ),
            "mlflow": MLflowConfig(enabled=False),
        }
    )

    summary = run_local_train(config)
    shipped = ROOT / "artifacts" / "models" / "best_model"
    shipped.mkdir(parents=True, exist_ok=True)
    if summary.model_bundle_dir and summary.model_bundle_dir != shipped:
        for name in ("model.joblib", "metadata.json"):
            src = summary.model_bundle_dir / name
            if src.exists():
                shutil.copy2(src, shipped / name)

    print(f"Model bundle ready at {shipped}")
    print(f"Metrics: {summary.metrics.get('test_metrics', {})}")


if __name__ == "__main__":
    main()
