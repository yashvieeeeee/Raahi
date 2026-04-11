from __future__ import annotations

import requests
from flask import current_app


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
            print(f"Error parsing user location: {exc}")

    token = current_app.config["WAQI_API_TOKEN"]
    if user_lat and user_lon:
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
            print(f"Location AQI lookup failed: {exc}")

    if aqi_data["aqi"] == 0 and aqi_data["pm25"] == 0 and aqi_data["pm10"] == 0:
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
            print(f"Mumbai AQI fallback failed: {exc}")
            aqi_data.update({"aqi": 107, "pm25": 107, "pm10": 66, "location": "Mumbai AQI baseline"})

    aqi_data["quality"] = _build_quality_label(aqi_data["aqi"])
    return aqi_data


def get_current_aqi_snapshot():
    try:
        headers = {"X-API-Key": current_app.config["OPENAQ_API_KEY"]}
        response = requests.get(
            "https://api.openaq.org/v3/measurements?location=3&parameter=pm25,pm10,aqi&limit=1&sortby=datetime&order=desc",
            headers=headers,
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                latest = data["results"][0]
                return {
                    "status": "success",
                    "location": "Mumbai (NMA)",
                    "timestamp": latest.get("datetime"),
                    "measurements": {
                        "pm25": latest.get("value", 0),
                        "pm10": next(
                            (item.get("value", 0) for item in data["results"] if item.get("parameter") == "pm10"),
                            0,
                        ),
                        "aqi": next(
                            (item.get("value", 0) for item in data["results"] if item.get("parameter") == "aqi"),
                            0,
                        ),
                    },
                }
        return {"status": "error", "message": "Unable to fetch AQI data"}
    except Exception as exc:
        return {"status": "error", "message": f"AQI API error: {exc}"}
