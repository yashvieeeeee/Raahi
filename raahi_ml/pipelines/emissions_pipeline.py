try:
    import pandas as pd
except ImportError:
    pd = None

from raahi_ml.config.paths import RAW_DATA_DIR


class EmissionsCalculator:
    def __init__(self):
        self.df = None
        if pd is not None:
            try:
                self.df = pd.read_csv(RAW_DATA_DIR / "vehicle_emission_dataset.csv")
            except Exception as exc:
                print(f"Error loading emissions dataset: {exc}")
        self.current_fuel_prices = self.get_realtime_fuel_prices()

    def get_realtime_fuel_prices(self):
        return {
            "Petrol": 106.04,
            "Diesel": 92.43,
            "Electric": 8.5,
            "Hybrid": 50.0,
        }

    def get_emission_data(
        self,
        vehicle_type,
        fuel_type,
        road_type="City",
        traffic="Moderate",
    ):
        if self.df is None:
            return None

        mask = (
            (self.df["Vehicle Type"] == vehicle_type)
            & (self.df["Fuel Type"] == fuel_type)
            & (self.df["Road Type"] == road_type)
            & (self.df["Traffic Conditions"] == traffic)
        )

        matching_data = self.df[mask]
        if len(matching_data) == 0:
            mask = (
                (self.df["Vehicle Type"] == vehicle_type)
                & (self.df["Fuel Type"] == fuel_type)
            )
            matching_data = self.df[mask]

        if len(matching_data) > 0:
            return matching_data.iloc[0]
        return None

    def calculate_co2_emissions(
        self,
        vehicle_type,
        fuel_type,
        distance_km,
        road_type="City",
        traffic="Moderate",
    ):
        emission_data = self.get_emission_data(
            vehicle_type,
            fuel_type,
            road_type,
            traffic,
        )

        if emission_data is not None:
            return emission_data["CO2 Emissions"] * distance_km

        fallback_emissions = {
            "Walk": 0,
            "Train": 41,
            "Bus": 89,
            "Auto": 150,
        }
        return fallback_emissions.get(vehicle_type, 100) * distance_km

    def calculate_trip_cost(
        self,
        vehicle_type,
        fuel_type,
        distance_km,
        road_type="City",
        traffic="Moderate",
    ):
        if vehicle_type == "Walk":
            return 0

        emission_data = self.get_emission_data(
            vehicle_type,
            fuel_type,
            road_type,
            traffic,
        )

        if emission_data is not None:
            mileage = emission_data["Mileage"]
            fuel_price = self.current_fuel_prices.get(fuel_type, 50)
            fuel_consumed = distance_km / mileage
            cost = fuel_consumed * fuel_price

            if vehicle_type == "Train":
                cost += 10
            elif vehicle_type == "Bus":
                cost += 15

            return round(cost, 2)

        fallback_costs = {
            "Train": distance_km * 2 + 10,
            "Bus": distance_km * 1.5 + 15,
            "Auto": 18 + distance_km * 12,
        }
        return fallback_costs.get(vehicle_type, 50)

    def calculate_travel_time(
        self,
        vehicle_type,
        distance_km,
        road_type="City",
        traffic="Moderate",
    ):
        emission_data = self.get_emission_data(
            vehicle_type,
            "Petrol",
            road_type,
            traffic,
        )

        if emission_data is not None and emission_data["Speed"] > 0:
            return (distance_km / emission_data["Speed"]) * 60

        speeds = {
            "Walk": 5,
            "Train": 40,
            "Bus": 20,
            "Auto": 25,
        }
        return (distance_km / speeds.get(vehicle_type, 25)) * 60

    def get_air_quality_impact(self, co2_emissions, pm25_emissions=0):
        co2_score = min(co2_emissions / 10, 100)
        pm25_score = min(pm25_emissions * 2, 100)
        return (co2_score + pm25_score) / 2


emissions_calculator = EmissionsCalculator()
