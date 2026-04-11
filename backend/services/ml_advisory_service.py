from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

from raahi_ml.config.paths import MODELS_DIR, PROCESSED_DATA_DIR


class AdvisoryModelService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.df = pd.DataFrame()
        self._load_assets()

    def _load_assets(self):
        try:
            self.model = joblib.load(MODELS_DIR / "model.pkl")
        except Exception as exc:
            print(f"Error loading advisory model: {exc}")

        try:
            self.label_encoder = joblib.load(MODELS_DIR / "label_encoder.pkl")
        except Exception as exc:
            print(f"Error loading label encoder: {exc}")

        try:
            self.df = pd.read_csv(PROCESSED_DATA_DIR / "raahi_with_predictions.csv")
        except Exception as exc:
            print(f"Error loading processed dataset: {exc}")

    def get_stations(self):
        if not self.df.empty and "station_name" in self.df.columns:
            return sorted(self.df["station_name"].dropna().unique().tolist())

        return [
            "CHURCHGATE",
            "MARINE LINES",
            "CHARNI ROAD",
            "GRANT ROAD",
            "MUMBAI CENTRAL",
            "LOWER PAREL",
            "PRABHADEVI",
            "DADAR",
            "MATUNGA ROAD",
            "MAHIM JN",
            "BANDRA",
            "KHAR ROAD",
            "SANTACRUZ",
            "VILE PARLE",
            "ANDHERI",
            "JOGESHWARI",
            "RAM MANDIR",
            "GOREGAON",
            "MALAD",
            "KANDIVALI",
            "BORIVALI",
            "DAHISAR",
            "MIRA ROAD",
            "NAIGAON",
            "VASAI ROAD",
            "NALLA SOPARA",
            "VIRAR",
        ]

    def predict_advisory(self, payload):
        hour = int(payload.get("hour", 8))
        crowd_grade = float(payload.get("crowd_grade", 1))
        congestion_perc = float(payload.get("congestion_perc", 45))
        aqi_value = int(payload.get("aqi_value", 185))
        is_raining = int(payload.get("is_raining", 0))
        flood_risk = int(payload.get("flood_risk", 0))
        is_peak = int(payload.get("is_peak", 0))
        avg_road_speed = float(payload.get("avg_road_speed", 40))
        predicted_delay = float(payload.get("predicted_delay", 5))
        passenger_count = int(payload.get("passenger_count", 1000))

        peak_hour_weight = 3.0 if hour in [8, 9, 18, 19] else 2.0 if hour in [7, 10, 17, 20] else 1.0
        log_passenger_count = np.log1p(passenger_count)
        speed_diff = avg_road_speed - (60 - predicted_delay)
        aqi_category = min(5, int(aqi_value // 80))
        monsoon_impact = round(
            min(0.5 * is_raining + congestion_perc / 200 + predicted_delay / 30 * 0.2, 1.0),
            4,
        )
        comfort_score = round(
            (1 - crowd_grade / 2) * 0.5 + (1 - is_raining) * 0.2 + (1 - aqi_category / 5) * 0.3,
            4,
        )
        pm25_emission_proxy = 0.106 if congestion_perc > 80 else 0.102 if congestion_perc > 40 else 0.103

        features = [
            hour,
            is_peak,
            peak_hour_weight,
            log_passenger_count,
            crowd_grade,
            congestion_perc,
            avg_road_speed,
            speed_diff,
            aqi_value,
            aqi_category,
            is_raining,
            monsoon_impact,
            flood_risk,
            comfort_score,
            predicted_delay,
            pm25_emission_proxy,
        ]

        if self.model is None:
            return {"advisory": "train_ok", "confidence": 50, "error": "Model not loaded"}

        prediction = self.model.predict([features])[0]
        if self.label_encoder is not None:
            try:
                advisory = self.label_encoder.inverse_transform([prediction])[0]
            except Exception:
                advisory = str(prediction)
        else:
            advisory = str(prediction)

        return {"advisory": advisory, "confidence": 75}


advisory_service = AdvisoryModelService()
