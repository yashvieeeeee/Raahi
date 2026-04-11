"""Flask routes exposing the newly added Raahi ML models."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from backend.services.ml_service import (
    get_available_models,
    get_delay_estimate,
    get_model_metrics,
    get_route_recommendation,
    get_transport_mode,
    retrain_model,
)


ml_blueprint = Blueprint("ml_routes", __name__)


def _admin_guard():
    if not getattr(current_user, "is_authenticated", False) or not getattr(current_user, "is_admin", False):
        return jsonify({"error": "Admin access required"}), 403
    return None


@ml_blueprint.post("/api/ml/predict-mode")
def predict_mode():
    """Return the predicted transport mode."""
    result = get_transport_mode(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.post("/api/ml/predict-delay")
def predict_delay_route():
    """Return the predicted station delay."""
    result = get_delay_estimate(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.post("/api/ml/recommend-route")
def recommend_route():
    """Return route recommendation classification."""
    result = get_route_recommendation(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.get("/api/ml/health")
@login_required
def ml_health():
    """Return health metadata for the ML model dashboard."""
    guard_response = _admin_guard()
    if guard_response:
        return guard_response

    return jsonify(
        {
            "status": "ok",
            "models": get_available_models(),
            "default_model": "model",
        }
    )


@ml_blueprint.get("/api/ml/metrics/<model_name>")
@login_required
def ml_metrics(model_name: str):
    """Return metrics for a single selected model."""
    guard_response = _admin_guard()
    if guard_response:
        return guard_response

    try:
        return jsonify(get_model_metrics(model_name))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ml_blueprint.post("/api/ml/retrain/<model_name>")
@login_required
def ml_retrain(model_name: str):
    """Retrain a selected model and return fresh metrics."""
    guard_response = _admin_guard()
    if guard_response:
        return guard_response

    try:
        return jsonify(retrain_model(model_name))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
