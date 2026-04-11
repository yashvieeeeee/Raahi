"""Backend service wrappers for the newly added Raahi ML models."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from raahi_ml.utils.model_loader import (
    predict_delay,
    predict_route_recommendation,
    predict_transport_mode,
)
from raahi_ml.config.ml_config import (
    DATA_RAW_PATH,
    MODELS_PATH,
    NEW_MODEL_NAMES,
    RANDOM_STATE,
    TEST_SIZE,
)
from raahi_ml.pipelines.model_metrics_pipeline import calculate_model_accuracy, get_current_metrics
from raahi_ml.pipelines.preprocess_new import (
    preprocess_behavioral,
    preprocess_route,
    preprocess_transport,
)
from raahi_ml.pipelines.train_new_models import (
    train_delay_model,
    train_route_model,
    train_transport_model,
)


METRICS_PATH = MODELS_PATH / "model_metrics.json"
LEGACY_MODEL_NAME = "model"
REGRESSION_MODELS = {"delay_predictor"}


def _load_metrics_store() -> dict:
    if not METRICS_PATH.exists():
        return {}
    try:
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_metrics_store(metrics_store: dict) -> None:
    METRICS_PATH.write_text(json.dumps(metrics_store, indent=2), encoding="utf-8")


def _has_legacy_metrics(metrics_store: dict) -> bool:
    required_keys = {"accuracy", "precision", "recall", "f1_score"}
    return required_keys.issubset(metrics_store.keys())


def _resolve_last_trained(model_name: str, metrics_store: dict) -> str:
    if model_name == LEGACY_MODEL_NAME:
        return metrics_store.get("last_trained") or metrics_store.get("calculation_time") or "N/A"
    model_entry = metrics_store.get(model_name, {})
    return model_entry.get("last_trained") or model_entry.get("trained_at") or "N/A"


def _resolve_version(model_name: str, metrics_store: dict) -> str:
    if model_name == LEGACY_MODEL_NAME:
        return str(metrics_store.get("model_version", "1.0.0"))
    model_entry = metrics_store.get(model_name, {})
    return str(model_entry.get("model_version") or model_entry.get("artifact") or model_name)


def _classification_payload(model_name: str, metrics_store: dict) -> dict:
    if model_name == LEGACY_MODEL_NAME:
        return {
            "name": LEGACY_MODEL_NAME,
            "task_type": "classification",
            "accuracy": float(metrics_store.get("accuracy", 0.0)),
            "precision": float(metrics_store.get("precision", 0.0)),
            "recall": float(metrics_store.get("recall", 0.0)),
            "f1_score": float(metrics_store.get("f1_score", 0.0)),
            "training_samples": int(metrics_store.get("training_samples", 0)),
            "last_trained": _resolve_last_trained(model_name, metrics_store),
            "version": _resolve_version(model_name, metrics_store),
        }

    model_entry = metrics_store.get(model_name, {})
    return {
        "name": model_name,
        "task_type": "classification",
        "accuracy": float(model_entry.get("accuracy", 0.0)),
        "precision": float(model_entry.get("precision", 0.0)),
        "recall": float(model_entry.get("recall", 0.0)),
        "f1_score": float(model_entry.get("f1_score", 0.0)),
        "training_samples": int(model_entry.get("training_samples", model_entry.get("rows", 0))),
        "last_trained": _resolve_last_trained(model_name, metrics_store),
        "version": _resolve_version(model_name, metrics_store),
    }


def _regression_payload(model_name: str, metrics_store: dict) -> dict:
    model_entry = metrics_store.get(model_name, {})
    return {
        "name": model_name,
        "task_type": "regression",
        "r2": float(model_entry.get("r2", model_entry.get("value", 0.0))),
        "mae": float(model_entry.get("mae", 0.0)),
        "rmse": float(model_entry.get("rmse", 0.0)),
        "training_samples": int(model_entry.get("training_samples", model_entry.get("rows", 0))),
        "last_trained": _resolve_last_trained(model_name, metrics_store),
        "version": _resolve_version(model_name, metrics_store),
    }


def _evaluate_transport_model() -> dict:
    dataset = pd.read_csv(DATA_RAW_PATH / "raw_transport_dataset.csv")
    features, target, _ = preprocess_transport(dataset)
    _, x_test, _, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=target,
    )
    model = joblib.load(MODELS_PATH / NEW_MODEL_NAMES["transport_mode_classifier"])
    predictions = model.predict(x_test)

    return {
        "task_type": "classification",
        "metric": "accuracy",
        "value": round(float(accuracy_score(y_test, predictions)), 4),
        "accuracy": round(float(accuracy_score(y_test, predictions) * 100), 2),
        "precision": round(
            float(precision_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "recall": round(
            float(recall_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "f1_score": round(
            float(f1_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "training_samples": int(len(dataset)),
        "last_trained": datetime.now(timezone.utc).isoformat(),
        "model_version": "1.0.0",
        "artifact": NEW_MODEL_NAMES["transport_mode_classifier"],
    }


def _evaluate_delay_model() -> dict:
    dataset = pd.read_csv(DATA_RAW_PATH / "Raahi_Behavioral_Chakachakit.csv")
    features, target, _ = preprocess_behavioral(dataset)
    _, x_test, _, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )
    model = joblib.load(MODELS_PATH / NEW_MODEL_NAMES["delay_predictor"])
    predictions = model.predict(x_test)
    rmse = math.sqrt(mean_squared_error(y_test, predictions))

    return {
        "task_type": "regression",
        "metric": "r2",
        "value": round(float(r2_score(y_test, predictions)), 4),
        "r2": round(float(r2_score(y_test, predictions)), 4),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 4),
        "rmse": round(float(rmse), 4),
        "training_samples": int(len(dataset)),
        "last_trained": datetime.now(timezone.utc).isoformat(),
        "model_version": "1.0.0",
        "artifact": NEW_MODEL_NAMES["delay_predictor"],
    }


def _evaluate_route_model() -> dict:
    dataset = pd.read_csv(DATA_RAW_PATH / "Raahi_Mumbai_Route_Transport_Noisy.csv")
    features, target, _ = preprocess_route(dataset)
    _, x_test, _, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=target,
    )
    model = joblib.load(MODELS_PATH / NEW_MODEL_NAMES["route_recommender"])
    predictions = model.predict(x_test)

    return {
        "task_type": "classification",
        "metric": "accuracy",
        "value": round(float(accuracy_score(y_test, predictions)), 4),
        "accuracy": round(float(accuracy_score(y_test, predictions) * 100), 2),
        "precision": round(
            float(precision_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "recall": round(
            float(recall_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "f1_score": round(
            float(f1_score(y_test, predictions, average="weighted", zero_division=0) * 100),
            2,
        ),
        "training_samples": int(len(dataset.dropna())),
        "last_trained": datetime.now(timezone.utc).isoformat(),
        "model_version": "1.0.0",
        "artifact": NEW_MODEL_NAMES["route_recommender"],
    }


def _persist_model_metrics(model_name: str, metrics_payload: dict) -> None:
    metrics_store = _load_metrics_store()
    model_entry = dict(metrics_store.get(model_name, {}))
    model_entry.update(metrics_payload)
    model_entry["last_trained"] = model_entry.get("last_trained") or model_entry.get("trained_at", "N/A")
    metrics_store[model_name] = model_entry
    _save_metrics_store(metrics_store)


def _refresh_new_model_metrics(model_name: str) -> dict:
    evaluators = {
        "transport_mode_classifier": _evaluate_transport_model,
        "delay_predictor": _evaluate_delay_model,
        "route_recommender": _evaluate_route_model,
    }
    if model_name not in evaluators:
        raise ValueError(f"Unknown model: {model_name}")

    metrics_payload = evaluators[model_name]()
    _persist_model_metrics(model_name, metrics_payload)
    metrics_store = _load_metrics_store()
    if model_name in REGRESSION_MODELS:
        return _regression_payload(model_name, metrics_store)
    return _classification_payload(model_name, metrics_store)


def _new_model_metrics_complete(model_name: str, metrics_store: dict) -> bool:
    model_entry = metrics_store.get(model_name, {})
    if not isinstance(model_entry, dict):
        return False

    if model_name in REGRESSION_MODELS:
        required_keys = {"r2", "mae", "rmse", "training_samples"}
    else:
        required_keys = {"accuracy", "precision", "recall", "f1_score", "training_samples"}
    return required_keys.issubset(model_entry.keys())


def get_available_models() -> list[str]:
    metrics_store = _load_metrics_store()
    model_names = []
    if _has_legacy_metrics(metrics_store):
        model_names.append(LEGACY_MODEL_NAME)

    for model_name, model_value in metrics_store.items():
        if isinstance(model_value, dict) and "artifact" in model_value:
            model_names.append(model_name)

    if not model_names:
        return [LEGACY_MODEL_NAME, "transport_mode_classifier", "delay_predictor", "route_recommender"]
    return model_names


def get_model_metrics(model_name: str) -> dict:
    metrics_store = _load_metrics_store()
    selected_model = model_name or LEGACY_MODEL_NAME

    if selected_model == LEGACY_MODEL_NAME:
        if not _has_legacy_metrics(metrics_store):
            metrics_store = get_current_metrics() or {}
        return _classification_payload(LEGACY_MODEL_NAME, metrics_store)

    if selected_model not in metrics_store or not _new_model_metrics_complete(selected_model, metrics_store):
        return _refresh_new_model_metrics(selected_model)

    if selected_model in REGRESSION_MODELS:
        return _regression_payload(selected_model, metrics_store)
    return _classification_payload(selected_model, metrics_store)


def retrain_model(model_name: str) -> dict:
    selected_model = model_name or LEGACY_MODEL_NAME

    if selected_model == LEGACY_MODEL_NAME:
        metrics = calculate_model_accuracy()
        if not metrics:
            raise ValueError("Legacy model retraining failed.")
        return get_model_metrics(LEGACY_MODEL_NAME)

    trainers = {
        "transport_mode_classifier": train_transport_model,
        "delay_predictor": train_delay_model,
        "route_recommender": train_route_model,
    }
    if selected_model not in trainers:
        raise ValueError(f"Unknown model: {selected_model}")

    trainers[selected_model]()
    return _refresh_new_model_metrics(selected_model)


def get_transport_mode(trip_data: dict) -> dict:
    """Predict transport mode from route and trip context."""
    try:
        return {
            "predicted_mode": predict_transport_mode(
                trip_data["source"],
                trip_data["destination"],
                trip_data["distance_km"],
                trip_data["travel_time_min"],
                trip_data["co2_kg"],
                trip_data["cost_rs"],
                trip_data["aqi"],
            )
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_delay_estimate(station_data: dict) -> dict:
    """Predict delay estimate from station conditions."""
    try:
        return {
            "predicted_delay_minutes": predict_delay(
                station_data["station_name"],
                station_data["passenger_count"],
                station_data["hour"],
                station_data["congestion_perc"],
                station_data["avg_road_speed"],
                station_data["aqi_value"],
                station_data["is_peak"],
                station_data["crowd_grade"],
                station_data["is_raining"],
            )
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_route_recommendation(route_data: dict) -> dict:
    """Predict whether a route should be recommended."""
    try:
        prediction = predict_route_recommendation(
            route_data["distance_km"],
            route_data["mode"],
            route_data["condition"],
            route_data["is_peak_hour"],
            route_data["is_raining"],
            route_data["travel_time_min"],
            route_data["co2_g"],
            route_data["cost_inr"],
            route_data["aqi"],
            route_data["comfort"],
            route_data["availability"],
        )
        return {"is_recommended": bool(prediction)}
    except Exception as exc:
        return {"error": str(exc)}
