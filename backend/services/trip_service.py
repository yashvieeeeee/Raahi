from backend.database.extensions import db
from backend.database.models import Trip
from raahi_ml.pipelines.emissions_pipeline import emissions_calculator


def save_user_location(user, payload):
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    if lat is None or lon is None:
        raise ValueError("Invalid coordinates")

    user.location = f"{lat},{lon}"
    user.location_enabled = True
    db.session.commit()
    return user.location


def save_trip_for_user(user, payload):
    trip = Trip(
        user_id=user.id,
        destination=payload["destination"],
        mode=payload["mode"],
        distance_km=payload["distance_km"],
        co2_emitted=payload["co2"],
        cost=payload["cost"],
    )
    db.session.add(trip)

    user.trips_taken += 1
    auto_co2 = emissions_calculator.calculate_co2_emissions(
        "Auto",
        "Petrol",
        payload["distance_km"],
        "City",
        "Moderate",
    )
    auto_cost = emissions_calculator.calculate_trip_cost(
        "Auto",
        "Petrol",
        payload["distance_km"],
        "City",
        "Moderate",
    )

    # Calculate savings - ensure minimum 0 CO2 and money (can't have negative savings)
    co2_delta = auto_co2 - payload["co2"]
    cost_delta = auto_cost - payload["cost"]
    
    user.co2_saved += max(0, co2_delta)  # Only add positive savings
    user.money_saved += max(0, cost_delta)  # Only add positive savings
    db.session.commit()
    return trip
