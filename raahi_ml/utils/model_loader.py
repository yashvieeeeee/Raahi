"""Helpers for loading and using the newly added Raahi ML models."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from raahi_ml.config.ml_config import MODELS_PATH, NEW_FEATURE_COLUMNS, NEW_MODEL_NAMES


def load_model(model_name: str):
    """Load a fitted model from the Raahi ML models directory."""
    file_name = NEW_MODEL_NAMES.get(model_name, model_name)
    return joblib.load(Path(MODELS_PATH) / file_name)


def load_encoder(encoder_name: str):
    """Load a fitted encoder from the Raahi ML models directory."""
    file_name = encoder_name if encoder_name.endswith(".pkl") else f"{encoder_name}.pkl"
    return joblib.load(Path(MODELS_PATH) / file_name)


def _encode_value(encoder_name: str, value):
    encoder = load_encoder(encoder_name)
    candidate = str(value)
    if candidate not in encoder.classes_:
        raise ValueError(f"Unknown label '{candidate}' for encoder '{encoder_name}'")
    return int(encoder.transform([candidate])[0])


def predict_transport_mode(source, destination, distance_km, travel_time_min, co2_kg, cost_rs, aqi) -> str:
    """Predict the most likely transport mode for a trip."""
    model = load_model("transport_mode_classifier")
    target_encoder = load_encoder("transport_enc_mode")

    payload = {
        "source_enc": _encode_value("transport_enc_source", source),
        "destination_enc": _encode_value("transport_enc_destination", destination),
        "distance_km": distance_km,
        "travel_time_min": travel_time_min,
        "co2_kg": co2_kg,
        "cost_rs": cost_rs,
        "aqi": aqi,
    }
    frame = pd.DataFrame([payload], columns=NEW_FEATURE_COLUMNS["transport_mode_classifier"])
    prediction = int(model.predict(frame)[0])
    return str(target_encoder.inverse_transform([prediction])[0])


def predict_delay(
    station_name,
    passenger_count,
    hour,
    congestion_perc,
    avg_road_speed,
    aqi_value,
    is_peak,
    crowd_grade,
    is_raining,
) -> float:
    """Predict expected delay in minutes for station conditions."""
    model = load_model("delay_predictor")
    payload = {
        "station_name_enc": _encode_value("delay_enc_station", station_name),
        "passenger_count": passenger_count,
        "hour": hour,
        "congestion_perc": congestion_perc,
        "avg_road_speed": avg_road_speed,
        "aqi_value": aqi_value,
        "is_peak": is_peak,
        "crowd_grade_enc": _encode_value("delay_enc_crowd_grade", crowd_grade),
        "is_raining": is_raining,
    }
    frame = pd.DataFrame([payload], columns=NEW_FEATURE_COLUMNS["delay_predictor"])
    return float(model.predict(frame)[0])


def predict_route_recommendation(
    distance_km,
    mode,
    condition,
    is_peak_hour,
    is_raining,
    travel_time_min,
    co2_g,
    cost_inr,
    aqi,
    comfort,
    availability,
) -> int:
    """Predict whether a route option should be recommended."""
    model = load_model("route_recommender")
    payload = {
        "distance_km": distance_km,
        "mode_enc": _encode_value("route_enc_mode", mode),
        "condition_enc": _encode_value("route_enc_condition", condition),
        "is_peak_hour": is_peak_hour,
        "is_raining": is_raining,
        "travel_time_min": travel_time_min,
        "co2_emissions_g": co2_g,
        "cost_inr": cost_inr,
        "aqi_at_destination": aqi,
        "comfort_score": comfort,
        "availability_score": availability,
    }
    frame = pd.DataFrame([payload], columns=NEW_FEATURE_COLUMNS["route_recommender"])
    return int(model.predict(frame)[0])

