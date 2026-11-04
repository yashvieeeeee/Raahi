from __future__ import annotations

import logging
import math
import requests
from flask import current_app

from backend.services.bus_fare_service import bus_fare_calculator
from raahi_ml.pipelines.emissions_pipeline import emissions_calculator

logger = logging.getLogger(__name__)

_GOOGLE_MAPS_DENIED = False

# Known Mumbai transit landmarks for instant geocoding without external network calls
MUMBAI_PRESETS = {
    "churchgate": (18.9322, 72.8264),
    "bandra": (19.0596, 72.8295),
    "bandra station": (19.0620, 72.8427),
    "andheri": (19.1136, 72.8697),
    "andheri west": (19.1363, 72.8277),
    "dadar": (19.0178, 72.8478),
    "cst": (18.9401, 72.8354),
    "chhatrapati shivaji terminus": (18.9401, 72.8354),
    "thane": (19.2183, 72.9781),
    "kurla": (19.0657, 72.8794),
    "marine drive": (18.9432, 72.8230),
    "navi mumbai": (19.0330, 73.0297),
    "borivali": (19.2288, 72.8541),
    "colaba": (18.9067, 72.8147),
}


def geocode_destination(destination):
    clean_dest = (destination or "").strip().lower()
    if clean_dest in MUMBAI_PRESETS:
        return MUMBAI_PRESETS[clean_dest]

    query = destination if "mumbai" in clean_dest else f"{destination}, Mumbai"
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={query}&format=json",
            headers={"User-Agent": "RaahiApp/1.0"},
            timeout=5,
        )
        if response.status_code == 200:
            geo_data = response.json()
            if geo_data:
                return float(geo_data[0]["lat"]), float(geo_data[0]["lon"])
    except Exception as exc:
        logger.warning("Nominatim geocoding failed for '%s': %s", destination, exc)

    raise ValueError("Destination not found")


def _haversine_road_distance(lat1, lon1, lat2, lon2) -> float:
    """Estimate driving road distance using Haversine multiplied by Mumbai road tortuosity factor (1.3)."""
    earth_radius_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return max(1.0, round(earth_radius_km * c * 1.3, 2))


def calculate_route_distance_km(user_lat, user_lon, dest_lat, dest_lon):
    global _GOOGLE_MAPS_DENIED
    google_key = current_app.config.get("GOOGLE_MAPS_API_KEY", "").strip()

    if google_key and not _GOOGLE_MAPS_DENIED:
        try:
            google_url = (
                "https://maps.googleapis.com/maps/api/directions/json"
                f"?origin={user_lat},{user_lon}"
                f"&destination={dest_lat},{dest_lon}"
                f"&mode=driving&key={google_key}&alternatives=true"
            )
            google_response = requests.get(google_url, timeout=5)
            if google_response.status_code == 200:
                google_data = google_response.json()
                status = google_data.get("status")
                if status == "OK" and google_data.get("routes"):
                    return google_data["routes"][0]["legs"][0]["distance"]["value"] / 1000
                if status in {"REQUEST_DENIED", "OVER_QUERY_LIMIT", "INVALID_REQUEST"}:
                    _GOOGLE_MAPS_DENIED = True
                    logger.warning(
                        "Google Maps API access returned %s. Switching cleanly to OSRM/Nominatim routing engine.",
                        status,
                    )
        except Exception as exc:
            _GOOGLE_MAPS_DENIED = True
            logger.warning("Google Maps route lookup failed: %s. Switching cleanly to OSRM/Nominatim.", exc)

    try:
        osrm_response = requests.get(
            f"https://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{dest_lon},{dest_lat}?overview=full",
            timeout=5,
        )
        if osrm_response.status_code == 200:
            osrm_data = osrm_response.json()
            if osrm_data.get("routes"):
                return osrm_data["routes"][0]["distance"] / 1000
    except Exception as exc:
        logger.warning("OSRM route lookup failed: %s. Falling back to road estimate.", exc)

    return _haversine_road_distance(user_lat, user_lon, dest_lat, dest_lon)


def get_route_recommendation(vehicle_type):
    recommendations = {
        "Walk": "Most eco-friendly option",
        "Train": "Fast and economical choice",
        "Auto": "Fastest but highest emissions",
    }
    return recommendations.get(vehicle_type, "Balanced travel option")


def build_route_options(user_lat, user_lon, dest_lat, dest_lon, distance_km):
    road_type = "City"
    traffic = "Heavy" if distance_km > 10 else "Moderate"
    route_options = []

    walk_co2 = emissions_calculator.calculate_co2_emissions("Walk", "Petrol", distance_km, road_type, traffic)
    walk_time = emissions_calculator.calculate_travel_time("Walk", distance_km, road_type, traffic)
    route_options.append(
        {
            "vehicle": "Walk",
            "time": walk_time,
            "cost": 0,
            "co2": walk_co2,
            "aqi_exposure": emissions_calculator.get_air_quality_impact(walk_co2, 0),
            "recommendation": get_route_recommendation("Walk"),
            "details": "Zero emissions, good for health",
        }
    )

    train_co2 = emissions_calculator.calculate_co2_emissions("Train", "Electric", distance_km, road_type, traffic)
    train_cost = emissions_calculator.calculate_trip_cost("Train", "Electric", distance_km, road_type, traffic)
    train_time = emissions_calculator.calculate_travel_time("Train", distance_km, road_type, traffic)
    route_options.append(
        {
            "vehicle": "Train",
            "time": train_time,
            "cost": train_cost,
            "co2": train_co2,
            "aqi_exposure": emissions_calculator.get_air_quality_impact(train_co2, 0),
            "recommendation": get_route_recommendation("Train"),
            "details": "Low emissions, reliable service",
        }
    )

    bus_info = bus_fare_calculator.get_bus_types()
    for bus_type in ["ordinary", "ac"]:
        bus_route_info = bus_fare_calculator.get_route_info(user_lat, user_lon, dest_lat, dest_lon, bus_type)
        bus_co2 = emissions_calculator.calculate_co2_emissions("Bus", "Electric", distance_km, road_type, traffic)
        route_options.append(
            {
                "vehicle": f"Bus - {bus_info[bus_type]['name']}",
                "time": bus_route_info["travel_time_minutes"],
                "cost": bus_route_info["fare"],
                "co2": bus_co2,
                "aqi_exposure": emissions_calculator.get_air_quality_impact(bus_co2, 0),
                "recommendation": bus_info[bus_type]["description"],
                "details": f"Fare: Rs.{bus_route_info['fare']}, Distance: {bus_route_info['distance_km']}km",
                "bus_type": bus_type,
                "bus_icon": bus_info[bus_type]["icon"],
                "bus_color": bus_info[bus_type]["color"],
                "nearest_depot": (bus_route_info.get("start_depot") or {}).get("name", "Unknown"),
                "end_depot": (bus_route_info.get("end_depot") or {}).get("name", "Unknown"),
            }
        )

    auto_co2 = emissions_calculator.calculate_co2_emissions("Auto", "Petrol", distance_km, road_type, traffic)
    auto_cost = emissions_calculator.calculate_trip_cost("Auto", "Petrol", distance_km, road_type, traffic)
    auto_time = emissions_calculator.calculate_travel_time("Auto", distance_km, road_type, traffic)
    route_options.append(
        {
            "vehicle": "Auto",
            "time": auto_time,
            "cost": auto_cost,
            "co2": auto_co2,
            "aqi_exposure": emissions_calculator.get_air_quality_impact(auto_co2, 0),
            "recommendation": get_route_recommendation("Auto"),
            "details": "Convenient door-to-door service",
        }
    )

    return route_options
