from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from backend.database.extensions import db
from backend.database.models import Trip
from backend.services.air_quality_service import get_aqi_for_user
from backend.services.home_service import build_home_dashboard_context
from backend.services.profile_service import build_profile_context
from backend.services.route_planner_service import (
    build_route_options,
    calculate_route_distance_km,
    geocode_destination,
)
from backend.services.trip_service import save_user_location


def register_web_routes(app):
    def _get_user_origin():
        raw_location = getattr(current_user, "location", None)
        if raw_location and "," in str(raw_location):
            try:
                lat_str, lon_str = str(raw_location).split(",", 1)
                return float(lat_str.strip()), float(lon_str.strip())
            except (TypeError, ValueError):
                pass
        return 19.0760, 72.8777

    @app.route("/location-permission")
    @login_required
    def location_permission():
        return render_template("location_permission.html")

    @app.route("/grant-location", methods=["POST"])
    @login_required
    def grant_location():
        current_user.location_enabled = True
        db.session.commit()
        return redirect(url_for("home"))

    @app.route("/save-location", methods=["POST"])
    @login_required
    def save_location():
        try:
            location = save_user_location(current_user, request.get_json() or {})
            return jsonify({"success": True, "message": "Location saved successfully", "location": location})
        except ValueError as exc:
            return jsonify({"success": False, "message": str(exc)}), 400
        except Exception as exc:
            return jsonify({"success": False, "message": f"Failed to save location: {exc}"}), 500

    @app.route("/home")
    @login_required
    def home():
        recent_trips = (
            Trip.query.filter_by(user_id=current_user.id)
            .order_by(Trip.timestamp.desc())
            .limit(5)
            .all()
        )
        aqi_data = get_aqi_for_user(current_user)
        return render_template(
            "home.html",
            user=current_user,
            aqi_data=aqi_data,
            **build_home_dashboard_context(current_user, aqi_data, recent_trips),
        )

    @app.route("/route-planner")
    @login_required
    def route_planner():
        destination = request.args.get("dest")
        if not destination:
            return redirect(url_for("home"))

        default_lat, default_lon = _get_user_origin()
        user_lat = float(request.args.get("lat", default_lat))
        user_lon = float(request.args.get("lon", default_lon))

        try:
            dest_lat, dest_lon = geocode_destination(destination)
        except ValueError:
            return "Destination not found", 404
        except Exception:
            return "Geocoding failed", 500

        distance_km = calculate_route_distance_km(user_lat, user_lon, dest_lat, dest_lon)
        routes = build_route_options(user_lat, user_lon, dest_lat, dest_lon, distance_km)

        return render_template(
            "route_planner.html",
            destination=destination,
            distance=distance_km,
            routes=routes,
            user_lat=user_lat,
            user_lon=user_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            max_time=max(route["time"] for route in routes),
            max_cost=max(route["cost"] for route in routes),
            max_co2=max(route["co2"] for route in routes),
            current_aqi=get_aqi_for_user(current_user)["aqi"],
        )

    @app.route("/map-navigation")
    @login_required
    def map_navigation():
        return render_template("map_navigation.html", route_data=request.args.to_dict())

    @app.route("/profile")
    @login_required
    def profile():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return render_template("profile.html", **build_profile_context(current_user))
