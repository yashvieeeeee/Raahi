"""Configuration for newly added Raahi ML training assets."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_RAW_PATH = BASE_DIR / "raahi_ml" / "data" / "raw"
DATA_PROCESSED_PATH = BASE_DIR / "raahi_ml" / "data" / "processed"
MODELS_PATH = BASE_DIR / "raahi_ml" / "models"

NEW_MODEL_NAMES = {
    "transport_mode_classifier": "transport_mode_classifier.pkl",
    "delay_predictor": "delay_predictor.pkl",
    "route_recommender": "route_recommender.pkl",
}

NEW_FEATURE_COLUMNS = {
    "transport_mode_classifier": [
        "source_enc",
        "destination_enc",
        "distance_km",
        "travel_time_min",
        "co2_kg",
        "cost_rs",
        "aqi",
    ],
    "delay_predictor": [
        "station_name_enc",
        "passenger_count",
        "hour",
        "congestion_perc",
        "avg_road_speed",
        "aqi_value",
        "is_peak",
        "crowd_grade_enc",
        "is_raining",
    ],
    "route_recommender": [
        "distance_km",
        "mode_enc",
        "condition_enc",
        "is_peak_hour",
        "is_raining",
        "travel_time_min",
        "co2_emissions_g",
        "cost_inr",
        "aqi_at_destination",
        "comfort_score",
        "availability_score",
    ],
}

RANDOM_STATE = 42
TEST_SIZE = 0.2

