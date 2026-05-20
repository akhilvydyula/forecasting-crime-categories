from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sitaka_api.config import SitakaConfig, load_config, write_config
from sitaka_api.services.workflows import (
    DeploymentService,
    EvaluationService,
    PredictionService,
    ProfileService,
    TrainingService,
)
from sitaka_api.sdk import SitakaClient

from crimecast.data import project_root
from crimecast.features import prepare_features_for_sitaka


@dataclass(frozen=True)
class SitakaRunSummary:
    mode: str
    model_bundle_dir: Path | None
    metrics: dict[str, Any]
    report_path: Path | None
    deployment_dir: Path | None


def default_config_path() -> Path:
    return project_root() / "config" / "sitaka.yaml"


def ensure_modeling_dataset() -> Path:
    return prepare_features_for_sitaka()


def load_or_create_config(config_path: Path | None = None) -> SitakaConfig:
    path = config_path or default_config_path()
    if path.exists():
        return load_config(path)
    ensure_modeling_dataset()
    config = SitakaConfig(
        project_name="crimecast-enterprise",
        task="tabular_classification",
        artifacts_dir=str(project_root() / "sitaka_artifacts"),
        data={
            "source": str(project_root() / "data" / "train_modeling.csv"),
            "format": "csv",
            "target": "Crime_Category",
            "test_size": 0.2,
            "random_state": 42,
        },
        exploration={"enabled": True, "report_name": "crimecast_eda.md"},
        automl={
            "enabled_models": ["random_forest", "extra_trees", "gradient_boosting", "linear"],
            "n_trials": 12,
            "cv_folds": 3,
            "max_rows": 15000,
        },
        mlflow={
            "enabled": True,
            "experiment_name": "crimecast-cbo",
            "tracking_uri": f"file:{project_root() / 'mlruns'}",
        },
        deployment={
            "framework": "streamlit",
            "output_dir": str(project_root() / "sitaka_deployment"),
        },
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    write_config(config, path, overwrite=True)
    return config


def run_local_profile(config: SitakaConfig | None = None) -> Path:
    cfg = config or load_or_create_config()
    ensure_modeling_dataset()
    result = ProfileService().profile(cfg)
    return result.report_path


def run_local_train(config: SitakaConfig | None = None) -> SitakaRunSummary:
    cfg = config or load_or_create_config()
    ensure_modeling_dataset()
    result = TrainingService().train(cfg)
    metrics_path = cfg.artifact_path / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    report_path = cfg.artifact_path / "reports" / cfg.exploration.report_name
    return SitakaRunSummary(
        mode="local",
        model_bundle_dir=result.model_bundle_dir,
        metrics=metrics,
        report_path=report_path if report_path.exists() else None,
        deployment_dir=None,
    )


def run_local_evaluate(config: SitakaConfig | None = None) -> dict[str, float]:
    cfg = config or load_or_create_config()
    return EvaluationService().evaluate(cfg).metrics


def run_local_predict(records: list[dict[str, Any]], config: SitakaConfig | None = None) -> list[str]:
    cfg = config or load_or_create_config()
    bundle = cfg.artifact_path / "models" / "best_model"
    if not bundle.exists():
        raise FileNotFoundError(
            "No trained model bundle found. Run training from the Model Lab page first."
        )
    return PredictionService().predict(bundle, records).predictions


def run_local_deploy(config: SitakaConfig | None = None, framework: str = "streamlit") -> Path:
    cfg = config or load_or_create_config()
    result = DeploymentService().deploy(cfg, framework=framework)
    return result.output_dir


def remote_client() -> SitakaClient:
    base_url = os.environ.get("SITAKA_API_URL", "http://127.0.0.1:8000")
    api_key = os.environ.get("SITAKA_API_KEY")
    return SitakaClient(base_url, api_key=api_key)


def remote_health() -> dict[str, Any]:
    import httpx

    client = remote_client()
    headers = {"X-API-Key": client.api_key} if client.api_key else {}
    with httpx.Client(base_url=client.base_url, timeout=client.timeout) as http:
        response = http.get("/v1/health", headers=headers)
        response.raise_for_status()
        return response.json()
