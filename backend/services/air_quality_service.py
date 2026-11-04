from __future__ import annotations

import logging
from datetime import datetime, timezone
import requests
from flask import current_app

logger = logging.getLogger(__name__)

# Fallback last-known AQI values (Mumbai baseline)
_LAST_KNOWN_AQI = {
    "aqi": 107,
    "pm25": 107,
    "pm10": 66,
    "location": "Mumbai",
    "timestamp": "2026-11-04T00:00:00+05:30",
}


def _build_quality_label(aqi_value: float) -> str:
    if aqi_value <= 50:
        return "Good - Safe for outdoor activities"
    if aqi_value <= 100:
        return "Moderate - Consider limiting prolonged outdoor exertion"
    if aqi_value <= 150:
        return "Unhealthy for sensitive groups"
    return "Very Unhealthy - Avoid outdoor activities"


def get_aqi_for_user(user):
    user_lat = None
    user_lon = None
    location_name = "Mumbai"
    aqi_data = {"aqi": 0, "pm25": 0, "pm10": 0, "quality": "Good", "location": location_name}

    if getattr(user, "location_enabled", False) and getattr(user, "location", None):
        try:
            if "," in user.location:
                parts = user.location.split(",")
                if len(parts) == 2:
                    user_lat = float(parts[0].strip())
                    user_lon = float(parts[1].strip())
                    location_name = f"Your Location ({user_lat:.2f}, {user_lon:.2f})"
                    aqi_data["location"] = location_name
        except Exception as exc:
            logger.warning("Error parsing user location: %s", exc)

    token = current_app.config.get("WAQI_API_TOKEN", "")
    if user_lat and user_lon and token:
        try:
            response = requests.get(
                f"https://api.waqi.info/feed/geo:{user_lat};{user_lon}/?token={token}",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and "data" in data:
                    station_data = data["data"]
                    iaqi = station_data.get("iaqi", {})
                    aqi_data.update(
                        {
                            "aqi": station_data.get("aqi", 0),
                            "pm25": iaqi.get("pm25", {}).get("v", 0),
                            "pm10": iaqi.get("pm10", {}).get("v", 0),
                            "location": station_data.get("city", {}).get("name", location_name),
                        }
                    )
        except Exception as exc:
            logger.warning("Location AQI lookup failed: %s", exc)

    if aqi_data["aqi"] == 0 and aqi_data["pm25"] == 0 and aqi_data["pm10"] == 0:
        if token:
            try:
                response = requests.get(
                    f"https://api.waqi.info/feed/@13715/?token={token}",
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok" and "data" in data:
                        station_data = data["data"]
                        iaqi = station_data.get("iaqi", {})
                        aqi_data.update(
                            {
                                "aqi": station_data.get("aqi", 107),
                                "pm25": iaqi.get("pm25", {}).get("v", 107),
                                "pm10": iaqi.get("pm10", {}).get("v", 66),
                                "location": station_data.get("city", {}).get("name", "Mumbai AQI baseline"),
                            }
                        )
            except Exception as exc:
                logger.warning("Mumbai AQI fallback failed: %s", exc)
                aqi_data.update({"aqi": 107, "pm25": 107, "pm10": 66, "location": "Mumbai AQI baseline"})
        else:
            aqi_data.update({"aqi": 107, "pm25": 107, "pm10": 66, "location": "Mumbai AQI baseline"})

    aqi_data["quality"] = _build_quality_label(aqi_data["aqi"])
    return aqi_data


def get_current_aqi_snapshot():
    """Retrieve current AQI snapshot using WAQI as primary, with cached last-known fallback."""
    global _LAST_KNOWN_AQI
    token = current_app.config.get("WAQI_API_TOKEN", "")

    if token:
        try:
            response = requests.get(
                f"https://api.waqi.info/feed/mumbai/?token={token}",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and "data" in data:
                    station_data = data["data"]
                    iaqi = station_data.get("iaqi", {})
                    aqi_val = station_data.get("aqi", 0)
                    pm25_val = iaqi.get("pm25", {}).get("v", aqi_val)
                    pm10_val = iaqi.get("pm10", {}).get("v", 0)
                    city_name = station_data.get("city", {}).get("name", "Mumbai")
                    timestamp = station_data.get("time", {}).get("iso", datetime.now(timezone.utc).isoformat())

                    _LAST_KNOWN_AQI = {
                        "aqi": aqi_val,
                        "pm25": pm25_val if pm25_val is not None else aqi_val,
                        "pm10": pm10_val if pm10_val is not None else 0,
                        "location": city_name,
                        "timestamp": timestamp,
                    }

                    return {
                        "status": "success",
                        "stale": False,
                        "location": _LAST_KNOWN_AQI["location"],
                        "timestamp": _LAST_KNOWN_AQI["timestamp"],
                        "measurements": {
                            "aqi": _LAST_KNOWN_AQI["aqi"],
                            "pm25": _LAST_KNOWN_AQI["pm25"],
                            "pm10": _LAST_KNOWN_AQI["pm10"],
                        },
                    }
        except Exception as exc:
            logger.warning("Live WAQI current AQI snapshot failed: %s", exc)

    # Graceful fallback: return cached values with stale=True and status 200
    return {
        "status": "success",
        "stale": True,
        "location": _LAST_KNOWN_AQI["location"],
        "timestamp": _LAST_KNOWN_AQI["timestamp"],
        "measurements": {
            "aqi": _LAST_KNOWN_AQI["aqi"],
            "pm25": _LAST_KNOWN_AQI["pm25"],
            "pm10": _LAST_KNOWN_AQI["pm10"],
        },
        "message": "Using cached AQI data due to upstream service unavailability",
    }
