"""Bus fare calculator for Mumbai BEST buses."""

from __future__ import annotations

import math

try:
    import pandas as pd
except ImportError:
    pd = None

from raahi_ml.config.paths import RAW_DATA_DIR

# Embedded verified Mumbai BEST bus depots (ensures zero pandas/file dependency on serverless)
DEFAULT_MUMBAI_BUS_DEPOTS: list[dict] = [
    {"name": "Colaba Bus Station", "geo_lat": 18.9147, "geo_long": 72.8258, "zone": "South Mumbai"},
    {"name": "Backbay Depot", "geo_lat": 18.9220, "geo_long": 72.8214, "zone": "South Mumbai"},
    {"name": "Mumbai Central Depot", "geo_lat": 18.9712, "geo_long": 72.8197, "zone": "South Mumbai"},
    {"name": "Worli Depot", "geo_lat": 19.0144, "geo_long": 72.8182, "zone": "South Mumbai"},
    {"name": "Wadala Depot", "geo_lat": 19.0225, "geo_long": 72.8584, "zone": "Central Mumbai"},
    {"name": "Dadar Bus Station", "geo_lat": 19.0178, "geo_long": 72.8478, "zone": "Central Mumbai"},
    {"name": "Dharavi Depot", "geo_lat": 19.0435, "geo_long": 72.8562, "zone": "Central Mumbai"},
    {"name": "Bandra Bus Station", "geo_lat": 19.0544, "geo_long": 72.8402, "zone": "Western Suburbs"},
    {"name": "Santacruz Depot", "geo_lat": 19.0833, "geo_long": 72.8417, "zone": "Western Suburbs"},
    {"name": "Andheri West Depot", "geo_lat": 19.1197, "geo_long": 72.8464, "zone": "Western Suburbs"},
    {"name": "Goregaon Bus Station", "geo_lat": 19.1553, "geo_long": 72.8492, "zone": "Western Suburbs"},
    {"name": "Dindoshi Depot", "geo_lat": 19.1742, "geo_long": 72.8604, "zone": "Western Suburbs"},
    {"name": "Poisar (Kandivali) Depot", "geo_lat": 19.2062, "geo_long": 72.8532, "zone": "Western Suburbs"},
    {"name": "Kurla Depot", "geo_lat": 19.0688, "geo_long": 72.8797, "zone": "Eastern Suburbs"},
    {"name": "Ghatkopar Depot", "geo_lat": 19.0860, "geo_long": 72.9090, "zone": "Eastern Suburbs"},
    {"name": "Vikhroli Depot", "geo_lat": 19.1112, "geo_long": 72.9281, "zone": "Eastern Suburbs"},
    {"name": "Mulund Depot", "geo_lat": 19.1765, "geo_long": 72.9555, "zone": "Eastern Suburbs"},
    {"name": "Deonar Depot", "geo_lat": 19.0522, "geo_long": 72.9125, "zone": "Eastern Suburbs"},
    {"name": "Majas (Jogeshwari) Depot", "geo_lat": 19.1354, "geo_long": 72.8682, "zone": "Western Suburbs"},
    {"name": "Borivali Station Depot", "geo_lat": 19.2288, "geo_long": 72.8541, "zone": "Western Suburbs"},
]


class BusFareCalculator:
    def __init__(self):
        self.bus_depots: list[dict] = []
        self.fare_structure = {
            "ordinary": {
                "base_fare": 5.0,
                "per_km": 2.0,
                "min_fare": 5.0,
                "max_fare": 15.0,
            },
            "express": {
                "base_fare": 10.0,
                "per_km": 3.0,
                "min_fare": 10.0,
                "max_fare": 25.0,
            },
            "ac": {
                "base_fare": 15.0,
                "per_km": 4.0,
                "min_fare": 15.0,
                "max_fare": 40.0,
            },
            "midi": {
                "base_fare": 6.0,
                "per_km": 2.5,
                "min_fare": 6.0,
                "max_fare": 20.0,
            },
        }
        self.load_bus_depots()

    def load_bus_depots(self):
        depots = list(DEFAULT_MUMBAI_BUS_DEPOTS)
        if pd is not None:
            csv_path = RAW_DATA_DIR / "bus_depots.csv"
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path)
                    if not df.empty:
                        depots = df.to_dict("records")
                except Exception as exc:
                    print(f"Error loading bus depots from CSV: {exc}")
        self.bus_depots = depots

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 0.0

        earth_radius_km = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius_km * c

    def find_nearest_depot(self, lat, lon):
        if not self.bus_depots or lat is None or lon is None:
            return None

        min_distance = float("inf")
        nearest_depot = None

        for depot in self.bus_depots:
            depot_lat = depot.get("geo_lat")
            depot_lon = depot.get("geo_long")
            if depot_lat is None or depot_lon is None:
                continue
            distance = self.calculate_distance(lat, lon, float(depot_lat), float(depot_lon))
            if distance < min_distance:
                min_distance = distance
                nearest_depot = dict(depot)
                nearest_depot["distance_km"] = round(distance, 2)

        return nearest_depot

    def calculate_fare(self, distance_km, bus_type="ordinary"):
        if bus_type not in self.fare_structure:
            bus_type = "ordinary"

        fare_config = self.fare_structure[bus_type]
        fare = fare_config["base_fare"] + (distance_km * fare_config["per_km"])
        fare = max(fare, fare_config["min_fare"])
        fare = min(fare, fare_config["max_fare"])
        return round(fare, 2)

    def get_bus_types(self):
        return {
            "ordinary": {
                "name": "Ordinary Bus",
                "description": "Regular non-AC bus service",
                "icon": "Bus",
                "color": "#ff6b6b",
            },
            "express": {
                "name": "Express Bus",
                "description": "Limited stops, faster service",
                "icon": "Express",
                "color": "#4ecdc4",
            },
            "ac": {
                "name": "AC Bus",
                "description": "Air-conditioned comfort",
                "icon": "AC",
                "color": "#45b7d1",
            },
            "midi": {
                "name": "Midi Bus",
                "description": "Smaller buses for narrow roads",
                "icon": "Midi",
                "color": "#96ceb4",
            },
        }

    def get_route_info(self, start_lat, start_lon, end_lat, end_lon, bus_type="ordinary"):
        distance = self.calculate_distance(start_lat, start_lon, end_lat, end_lon)
        fare = self.calculate_fare(distance, bus_type)
        start_depot = self.find_nearest_depot(start_lat, start_lon)
        end_depot = self.find_nearest_depot(end_lat, end_lon)
        travel_time = (distance / 20.0) * 60
        co2_emission = distance * 0.8 * 1000

        return {
            "distance_km": round(distance, 2),
            "fare": fare,
            "travel_time_minutes": round(travel_time),
            "co2_emission_grams": round(co2_emission),
            "bus_type": bus_type,
            "start_depot": start_depot,
            "end_depot": end_depot,
            "bus_info": self.get_bus_types().get(bus_type, {}),
        }

    def get_all_depots(self):
        return list(self.bus_depots)


bus_fare_calculator = BusFareCalculator()
