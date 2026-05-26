"""Flask routes exposing the newly added Raahi ML models."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required


ml_blueprint = Blueprint("ml_routes", __name__)


def _load_ml_service():
    try:
        from backend.services import ml_service

        return ml_service
    except Exception as exc:
        return exc


def _ml_unavailable(exc):
    return jsonify(
        {
            "error": "ML features are unavailable in this deployment.",
            "details": str(exc),
        }
    ), 503


def _admin_guard():
    if not getattr(current_user, "is_authenticated", False) or not getattr(current_user, "is_admin", False):
        return jsonify({"error": "Admin access required"}), 403
    return None


@ml_blueprint.post("/api/ml/predict-mode")
def predict_mode():
    """Return the predicted transport mode."""
    service = _load_ml_service()
    if isinstance(service, Exception):
        return _ml_unavailable(service)

    result = service.get_transport_mode(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.post("/api/ml/predict-delay")
def predict_delay_route():
    """Return the predicted station delay."""
    service = _load_ml_service()
    if isinstance(service, Exception):
        return _ml_unavailable(service)

    result = service.get_delay_estimate(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.post("/api/ml/recommend-route")
def recommend_route():
    """Return route recommendation classification."""
    service = _load_ml_service()
    if isinstance(service, Exception):
        return _ml_unavailable(service)

    result = service.get_route_recommendation(request.get_json() or {})
    return jsonify(result), 400 if "error" in result else 200


@ml_blueprint.get("/api/ml/health")
@login_required
def ml_health():
    """Return health metadata for the ML model dashboard."""
    guard_response = _admin_guard()
    if guard_response:
        return guard_response

    service = _load_ml_service()
    if isinstance(service, Exception):
        return _ml_unavailable(service)

    return jsonify(
        {
            "status": "ok",
            "models": service.get_available_models(),
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
        service = _load_ml_service()
        if isinstance(service, Exception):
            return _ml_unavailable(service)

        return jsonify(service.get_model_metrics(model_name))
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
        service = _load_ml_service()
        if isinstance(service, Exception):
            return _ml_unavailable(service)

        return jsonify(service.retrain_model(model_name))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
