from __future__ import annotations

import math
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from backend.database.extensions import db
from backend.database.models import Trip
from raahi_ml.pipelines.emissions_pipeline import emissions_calculator


def save_user_location(user, payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid payload: expected JSON object")

    lat = payload.get("latitude")
    lon = payload.get("longitude")
    if lat is None or lon is None:
        raise ValueError("Invalid coordinates: latitude and longitude are required")

    try:
        lat_f = float(lat)
        lon_f = float(lon)
        if math.isnan(lat_f) or math.isinf(lat_f) or math.isnan(lon_f) or math.isinf(lon_f):
            raise ValueError()
        if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError("Invalid coordinates: latitude must be in [-90, 90] and longitude in [-180, 180]")

    user.location = f"{lat_f},{lon_f}"
    user.location_enabled = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return user.location


def _validate_numeric(
    val: Any,
    field_name: str,
    min_val: float = 0.0,
    max_val: float = 100000.0,
    allow_zero: bool = True,
) -> float:
    try:
        num = float(val)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}: numeric value required")
    if math.isnan(num) or math.isinf(num):
        raise ValueError(f"Invalid {field_name}: finite number required")
    if num < min_val or (not allow_zero and num <= min_val) or num > max_val:
        comparator = ">=" if allow_zero else ">"
        raise ValueError(f"Invalid {field_name}: must be {comparator} {min_val} and <= {max_val}")
    return num


def save_trip_for_user(user, payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid payload: expected JSON object")

    destination = str(payload.get("destination") or "").strip()
    if not destination or len(destination) > 255:
        raise ValueError("Invalid destination: non-empty string under 255 characters required")

    mode = str(payload.get("mode") or "").strip()
    if not mode or len(mode) > 64:
        raise ValueError("Invalid mode: non-empty string under 64 characters required")

    distance_km = _validate_numeric(
        payload.get("distance_km"),
        "distance_km",
        min_val=0.0,
        max_val=10000.0,
        allow_zero=False,
    )
    co2 = _validate_numeric(
        payload.get("co2"),
        "co2",
        min_val=0.0,
        max_val=1000000.0,
        allow_zero=True,
    )
    cost = _validate_numeric(
        payload.get("cost"),
        "cost",
        min_val=0.0,
        max_val=1000000.0,
        allow_zero=True,
    )

    trip = Trip(
        user_id=user.id,
        destination=destination,
        mode=mode,
        distance_km=distance_km,
        co2_emitted=co2,
        cost=cost,
    )
    db.session.add(trip)

    user.trips_taken += 1
    auto_co2 = emissions_calculator.calculate_co2_emissions(
        "Auto",
        "Petrol",
        distance_km,
        "City",
        "Moderate",
    )
    auto_cost = emissions_calculator.calculate_trip_cost(
        "Auto",
        "Petrol",
        distance_km,
        "City",
        "Moderate",
    )

    # Calculate savings - ensure minimum 0 CO2 and money (can't have negative savings)
    co2_delta = auto_co2 - co2
    cost_delta = auto_cost - cost

    user.co2_saved += max(0.0, co2_delta)  # Only add positive savings
    user.money_saved += max(0.0, cost_delta)  # Only add positive savings

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return trip
