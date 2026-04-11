"""Preprocessing helpers for the new Raahi ML models."""

from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from raahi_ml.config.ml_config import NEW_FEATURE_COLUMNS


def preprocess_transport(df: pd.DataFrame):
    """Prepare transport mode classification features, target, and encoders."""
    cleaned_df = df.copy()

    source_encoder = LabelEncoder()
    destination_encoder = LabelEncoder()
    mode_encoder = LabelEncoder()

    cleaned_df["source_enc"] = source_encoder.fit_transform(cleaned_df["source"].astype(str))
    cleaned_df["destination_enc"] = destination_encoder.fit_transform(
        cleaned_df["destination"].astype(str)
    )
    y = mode_encoder.fit_transform(cleaned_df["mode"].astype(str))

    x = cleaned_df[NEW_FEATURE_COLUMNS["transport_mode_classifier"]].copy()
    encoders = {
        "transport_enc_source": source_encoder,
        "transport_enc_destination": destination_encoder,
        "transport_enc_mode": mode_encoder,
    }
    return x, y, encoders


def preprocess_behavioral(df: pd.DataFrame):
    """Prepare delay regression features, target, and encoders."""
    cleaned_df = df.copy()

    station_encoder = LabelEncoder()
    crowd_grade_encoder = LabelEncoder()

    cleaned_df["station_name_enc"] = station_encoder.fit_transform(
        cleaned_df["station_name"].astype(str)
    )
    cleaned_df["crowd_grade_enc"] = crowd_grade_encoder.fit_transform(
        cleaned_df["crowd_grade"].astype(str)
    )

    x = cleaned_df[NEW_FEATURE_COLUMNS["delay_predictor"]].copy()
    y = cleaned_df["predicted_delay"].copy()
    encoders = {
        "delay_enc_station": station_encoder,
        "delay_enc_crowd_grade": crowd_grade_encoder,
    }
    return x, y, encoders


def preprocess_route(df: pd.DataFrame):
    """Prepare route recommendation features, target, and encoders."""
    cleaned_df = df.dropna().copy()

    mode_encoder = LabelEncoder()
    condition_encoder = LabelEncoder()

    cleaned_df["mode_enc"] = mode_encoder.fit_transform(cleaned_df["mode"].astype(str))
    cleaned_df["condition_enc"] = condition_encoder.fit_transform(
        cleaned_df["condition"].astype(str)
    )

    x = cleaned_df[NEW_FEATURE_COLUMNS["route_recommender"]].copy()
    y = cleaned_df["is_recommended"].astype(int).copy()
    encoders = {
        "route_enc_mode": mode_encoder,
        "route_enc_condition": condition_encoder,
    }
    return x, y, encoders

