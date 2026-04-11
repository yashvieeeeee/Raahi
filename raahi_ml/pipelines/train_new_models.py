"""Standalone training script for newly added Raahi ML models."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from raahi_ml.config.ml_config import (
    DATA_RAW_PATH,
    MODELS_PATH,
    NEW_MODEL_NAMES,
    RANDOM_STATE,
    TEST_SIZE,
)
from raahi_ml.pipelines.preprocess_new import (
    preprocess_behavioral,
    preprocess_route,
    preprocess_transport,
)


def _save_encoders(encoders: dict) -> None:
    for encoder_name, encoder in encoders.items():
        joblib.dump(encoder, MODELS_PATH / f"{encoder_name}.pkl")


def _append_metrics(new_metrics: dict) -> None:
    metrics_path = MODELS_PATH / "model_metrics.json"
    with metrics_path.open("r", encoding="utf-8") as handle:
        existing_metrics = json.load(handle)

    existing_metrics.update(new_metrics)

    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(existing_metrics, handle, indent=2)


def train_transport_model():
    """Train and save the transport mode classifier."""
    dataset = pd.read_csv(DATA_RAW_PATH / "raw_transport_dataset.csv")
    x, y, encoders = preprocess_transport(dataset)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = XGBClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        eval_metric="mlogloss",
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    joblib.dump(model, MODELS_PATH / NEW_MODEL_NAMES["transport_mode_classifier"])
    _save_encoders(encoders)
    return {
        "transport_mode_classifier": {
            "metric": "accuracy",
            "value": round(float(accuracy), 4),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "rows": int(len(dataset)),
            "artifact": NEW_MODEL_NAMES["transport_mode_classifier"],
        }
    }


def train_delay_model():
    """Train and save the delay predictor."""
    dataset = pd.read_csv(DATA_RAW_PATH / "Raahi_Behavioral_Chakachakit.csv")
    x, y, encoders = preprocess_behavioral(dataset)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    model = GradientBoostingRegressor(
        n_estimators=100,
        random_state=RANDOM_STATE,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    score = r2_score(y_test, predictions)

    joblib.dump(model, MODELS_PATH / NEW_MODEL_NAMES["delay_predictor"])
    _save_encoders(encoders)
    return {
        "delay_predictor": {
            "metric": "r2",
            "value": round(float(score), 4),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "rows": int(len(dataset)),
            "artifact": NEW_MODEL_NAMES["delay_predictor"],
        }
    }


def train_route_model():
    """Train and save the route recommendation classifier."""
    dataset = pd.read_csv(DATA_RAW_PATH / "Raahi_Mumbai_Route_Transport_Noisy.csv")
    x, y, encoders = preprocess_route(dataset)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    joblib.dump(model, MODELS_PATH / NEW_MODEL_NAMES["route_recommender"])
    _save_encoders(encoders)
    return {
        "route_recommender": {
            "metric": "accuracy",
            "value": round(float(accuracy), 4),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "rows": int(len(dataset.dropna())),
            "artifact": NEW_MODEL_NAMES["route_recommender"],
        }
    }


def main():
    """Train all new models while isolating failures."""
    trainers = [
        ("transport_mode_classifier", train_transport_model),
        ("delay_predictor", train_delay_model),
        ("route_recommender", train_route_model),
    ]
    collected_metrics = {}
    summary_rows = []

    for logical_name, trainer in trainers:
        try:
            result = trainer()
            collected_metrics.update(result)
            metric_name = result[logical_name]["metric"]
            metric_value = result[logical_name]["value"]
            summary_rows.append((logical_name, metric_name, metric_value, "ok"))
        except Exception as exc:
            summary_rows.append((logical_name, "error", str(exc), "failed"))

    if collected_metrics:
        _append_metrics(collected_metrics)

    print("\nNew Model Training Summary")
    print("-" * 72)
    print(f"{'model':30} {'metric':12} {'value':18} {'status':10}")
    print("-" * 72)
    for model_name, metric_name, metric_value, status in summary_rows:
        print(f"{model_name:30} {metric_name:12} {str(metric_value):18} {status:10}")


if __name__ == "__main__":
    main()
