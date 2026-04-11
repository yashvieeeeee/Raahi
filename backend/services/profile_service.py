from datetime import datetime, timedelta

from backend.database.models import Trip


def build_profile_context(user):
    all_trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.timestamp.desc()).all()
    all_trips_data = [
        {
            "id": trip.id,
            "destination": trip.destination,
            "mode": trip.mode,
            "distance_km": trip.distance_km,
            "co2_emitted": trip.co2_emitted,
            "cost": trip.cost,
            "timestamp": trip.timestamp.isoformat() if trip.timestamp else None,
        }
        for trip in all_trips
    ]

    total_co2_saved = float(user.co2_saved or 0)
    total_money_saved = float(user.money_saved or 0)

    weekly_trips = (
        Trip.query.filter_by(user_id=user.id)
        .filter(Trip.timestamp >= datetime.utcnow() - timedelta(days=7))
        .all()
    )
    weekly_co2 = []
    for index in range(7):
        date = datetime.utcnow() - timedelta(days=6 - index)
        day_trips = [trip for trip in weekly_trips if trip.timestamp.date() == date.date()]
        weekly_co2.append(sum(trip.co2_emitted for trip in day_trips))

    monthly_trips = (
        Trip.query.filter_by(user_id=user.id)
        .filter(Trip.timestamp >= datetime.utcnow() - timedelta(days=30))
        .all()
    )
    monthly_co2 = []
    for index in range(4):
        week_start = datetime.utcnow() - timedelta(weeks=3 - index)
        week_end = week_start + timedelta(days=6)
        week_trips = [trip for trip in monthly_trips if week_start <= trip.timestamp <= week_end]
        monthly_co2.append(sum(trip.co2_emitted for trip in week_trips))

    return {
        "user": user,
        "all_trips": all_trips,
        "all_trips_data": all_trips_data,
        "total_co2_saved": total_co2_saved,
        "total_money_saved": total_money_saved,
        "weekly_co2": weekly_co2,
        "monthly_co2": monthly_co2,
    }
