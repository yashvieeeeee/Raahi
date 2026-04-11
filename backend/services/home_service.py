"""User dashboard context helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from backend.database.models import Trip


ECO_MODES = {"train", "metro", "bus", "walk", "bike", "ferry"}


def _parse_user_location(user) -> tuple[float | None, float | None]:
    raw_location = getattr(user, "location", None)
    if not raw_location or "," not in str(raw_location):
        return None, None

    try:
        lat_str, lon_str = str(raw_location).split(",", 1)
        return float(lat_str.strip()), float(lon_str.strip())
    except (TypeError, ValueError):
        return None, None


def _build_weekly_trip_activity(trips: list[Trip]) -> list[dict]:
    daily_counts = []
    for offset in range(6, -1, -1):
        target_date = datetime.utcnow().date() - timedelta(days=offset)
        count = sum(1 for trip in trips if trip.timestamp and trip.timestamp.date() == target_date)
        daily_counts.append({"label": target_date.strftime("%a"), "value": count})
    return daily_counts


def _build_mode_counts(trips: list[Trip]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for trip in trips:
        mode = trip.mode or "Unknown"
        counts[mode] = counts.get(mode, 0) + 1
    return counts


def _build_mode_mix(trips: list[Trip]) -> list[dict]:
    counts = _build_mode_counts(trips)
    return [{"label": label, "value": value} for label, value in counts.items()]


def _average_trip_cost(trips: list[Trip]) -> float:
    if not trips:
        return 0.0
    return round(sum(float(trip.cost or 0) for trip in trips) / len(trips), 1)


def _calculate_trip_streak(trips: list[Trip]) -> int:
    unique_days = sorted(
        {trip.timestamp.date() for trip in trips if trip.timestamp},
        reverse=True,
    )
    if not unique_days:
        return 0

    streak = 0
    expected_day = unique_days[0]
    for trip_day in unique_days:
        if trip_day != expected_day:
            break
        streak += 1
        expected_day -= timedelta(days=1)
    return streak


def _aqi_tone(aqi: int) -> str:
    if aqi <= 100:
        return "success"
    if aqi <= 150:
        return "warning"
    return "danger"


def _aqi_focus(aqi: int) -> str:
    if aqi <= 80:
        return "Clean travel window"
    if aqi <= 120:
        return "Moderate air caution"
    return "High exposure watch"


def _build_workspace_highlights(aqi_data: dict, monthly_trips: list[Trip]) -> list[dict]:
    mode_counts = _build_mode_counts(monthly_trips)
    total_modes = sum(mode_counts.values()) or 1
    clean_trip_share = round(
        sum(
            count
            for label, count in mode_counts.items()
            if str(label).strip().lower() in ECO_MODES
        )
        / total_modes
        * 100
    )
    streak = _calculate_trip_streak(monthly_trips)
    aqi = int(aqi_data.get("aqi", 0) or 0)

    return [
        {
            "label": "Clean trip share",
            "value": f"{clean_trip_share}%",
            "meta": "Rail, bus, and walk-led trips this month",
            "badge": "Eco first",
            "tone": "success" if clean_trip_share >= 60 else "warning",
        },
        {
            "label": "AQI focus",
            "value": f"AQI {aqi}",
            "meta": _aqi_focus(aqi),
            "badge": aqi_data.get("quality", "Air watch"),
            "tone": _aqi_tone(aqi),
        },
        {
            "label": "Trip streak",
            "value": f"{streak} day{'s' if streak != 1 else ''}",
            "meta": "Consecutive commute logging rhythm",
            "badge": "Momentum",
            "tone": "info" if streak >= 3 else "warning",
        },
    ]


def _build_insights(user, aqi_data: dict, recent_trips: list[Trip]) -> list[dict]:
    aqi = int(aqi_data.get("aqi", 0) or 0)
    insights = [
        {
            "title": "AQI-aware routing",
            "body": f"{aqi_data.get('quality', 'AQI stable')} around {aqi_data.get('location', 'your area')}. Keep low-exposure rail and walk segments near the top of your shortlist.",
            "tone": _aqi_tone(aqi),
        },
        {
            "title": "Impact momentum",
            "body": f"You have saved Rs.{round(float(user.money_saved or 0))} across {user.trips_taken or 0} eco trips, which is building a stronger low-emission routine.",
            "tone": "success",
        },
    ]
    if recent_trips:
        latest_trip = recent_trips[0]
        insights.append(
            {
                "title": "Latest route pattern",
                "body": f"Your last saved trip to {latest_trip.destination} used {latest_trip.mode}. Re-run that route when AQI spikes to compare cleaner alternatives side by side.",
                "tone": "info",
            }
        )
    else:
        insights.append(
            {
                "title": "Unlock your dashboard",
                "body": "Save your first trip to activate richer weekly analytics, route suggestions, and personalized impact tracking.",
                "tone": "warning",
            }
        )
    return insights


def _build_commute_signals(user, aqi_data: dict, monthly_trips: list[Trip]) -> list[dict]:
    weekly_trips = sum(item["value"] for item in _build_weekly_trip_activity(monthly_trips))
    avg_trip_cost = _average_trip_cost(monthly_trips)
    mode_counts = _build_mode_counts(monthly_trips)
    total_modes = sum(mode_counts.values()) or 1
    clean_share = round(
        sum(
            count
            for label, count in mode_counts.items()
            if str(label).strip().lower() in ECO_MODES
        )
        / total_modes
        * 100
    )
    aqi = int(aqi_data.get("aqi", 0) or 0)
    aqi_readiness = max(8, min(100, round(100 - ((aqi - 40) / 160) * 100)))
    savings_pace = min(round((float(user.co2_saved or 0) / 20000) * 100), 100)
    weekly_pulse = min(round((weekly_trips / 10) * 100), 100)
    budget_efficiency = max(12, min(100, round(100 - min(avg_trip_cost, 120))))

    return [
        {
            "label": "Low-emission mode balance",
            "value": f"{clean_share}%",
            "progress": clean_share,
            "tone": "success" if clean_share >= 60 else "warning",
            "meta": "Share of recent trips taken by rail, bus, walk, bike, or ferry.",
        },
        {
            "label": "Weekly commute pulse",
            "value": f"{weekly_trips} trips",
            "progress": weekly_pulse,
            "tone": "info",
            "meta": "Trip logging frequency over the past 7 days.",
        },
        {
            "label": "CO2 savings pace",
            "value": f"{round(float(user.co2_saved or 0) / 1000, 2)} kg",
            "progress": savings_pace,
            "tone": "success",
            "meta": "Progress toward the current personal impact target.",
        },
        {
            "label": "AQI readiness",
            "value": _aqi_focus(aqi),
            "progress": aqi_readiness,
            "tone": _aqi_tone(aqi),
            "meta": "Higher scores mean your current conditions are friendlier for outdoor transfer segments.",
        },
        {
            "label": "Trip spend efficiency",
            "value": f"Rs.{avg_trip_cost}",
            "progress": budget_efficiency,
            "tone": "warning" if avg_trip_cost > 70 else "success",
            "meta": "Average saved-trip cost this month compared with a lighter-spend target.",
        },
    ]


def _build_recommended_focus(aqi_data: dict, monthly_trips: list[Trip]) -> str:
    aqi = int(aqi_data.get("aqi", 0) or 0)
    avg_trip_cost = _average_trip_cost(monthly_trips)
    if aqi > 120:
        return "Prefer low-exposure rail transfers today"
    if avg_trip_cost > 70:
        return "Trim spend with mixed rail and walk segments"
    return "Keep the balanced eco-route streak going"


def build_home_dashboard_context(user, aqi_data: dict, recent_trips: list[Trip]) -> dict:
    monthly_trips = (
        Trip.query.filter_by(user_id=user.id)
        .filter(Trip.timestamp >= datetime.utcnow() - timedelta(days=30))
        .order_by(Trip.timestamp.desc())
        .all()
    )
    avg_trip_cost = _average_trip_cost(monthly_trips)
    user_origin_lat, user_origin_lon = _parse_user_location(user)

    return {
        "recent_trips": recent_trips,
        "weekly_trip_activity": _build_weekly_trip_activity(monthly_trips),
        "mode_mix": _build_mode_mix(monthly_trips),
        "insights": _build_insights(user, aqi_data, recent_trips),
        "workspace_highlights": _build_workspace_highlights(aqi_data, monthly_trips),
        "commute_signals": _build_commute_signals(user, aqi_data, monthly_trips),
        "recommended_focus": _build_recommended_focus(aqi_data, monthly_trips),
        "monthly_trip_count": len(monthly_trips),
        "avg_trip_cost": avg_trip_cost,
        "user_origin_lat": user_origin_lat,
        "user_origin_lon": user_origin_lon,
    }
