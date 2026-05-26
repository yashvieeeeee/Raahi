"""Bus fare calculator for Mumbai BEST buses."""

import math

try:
    import pandas as pd
except ImportError:
    pd = None

from raahi_ml.config.paths import RAW_DATA_DIR


class BusFareCalculator:
    def __init__(self):
        self.bus_depots = None
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
        if pd is None:
            self.bus_depots = []
            return

        try:
            self.bus_depots = pd.read_csv(RAW_DATA_DIR / "bus_depots.csv")
        except Exception as exc:
            print(f"Error loading bus depots: {exc}")
            self.bus_depots = pd.DataFrame()

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
        if pd is None or self.bus_depots.empty or lat is None or lon is None:
            return None

        min_distance = float("inf")
        nearest_depot = None

        for _, depot in self.bus_depots.iterrows():
            distance = self.calculate_distance(lat, lon, depot["geo_lat"], depot["geo_long"])
            if distance < min_distance:
                min_distance = distance
                nearest_depot = depot

        return nearest_depot.to_dict() if nearest_depot is not None else None

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
        if pd is None or self.bus_depots.empty:
            return []
        return self.bus_depots.to_dict("records")


bus_fare_calculator = BusFareCalculator()
