from __future__ import annotations

import requests
from flask import current_app

from backend.services.bus_fare_service import bus_fare_calculator
from raahi_ml.pipelines.emissions_pipeline import emissions_calculator


def geocode_destination(destination):
    response = requests.get(
        f"https://nominatim.openstreetmap.org/search?q={destination}&format=json",
        headers={"User-Agent": "RaahiApp/1.0"},
        timeout=5,
    )
    geo_data = response.json()
    if not geo_data:
        raise ValueError("Destination not found")
    return float(geo_data[0]["lat"]), float(geo_data[0]["lon"])


def calculate_route_distance_km(user_lat, user_lon, dest_lat, dest_lon):
    google_key = current_app.config["GOOGLE_MAPS_API_KEY"]
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
            if "routes" in google_data and google_data["routes"]:
                return google_data["routes"][0]["legs"][0]["distance"]["value"] / 1000
    except Exception as exc:
        print(f"Google Maps route lookup failed: {exc}")

    try:
        osrm_response = requests.get(
            f"https://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{dest_lon},{dest_lat}?overview=full",
            timeout=5,
        )
        osrm_data = osrm_response.json()
        return osrm_data["routes"][0]["distance"] / 1000
    except Exception as exc:
        print(f"OSRM route lookup failed: {exc}")
        return 10.0


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
