from flask import jsonify, request
from flask_login import current_user, login_required

from backend.services.air_quality_service import get_current_aqi_snapshot
from backend.services.bus_fare_service import bus_fare_calculator
from backend.services.ml_advisory_service import advisory_service
from backend.services.trip_service import save_trip_for_user


def register_api_routes(app):
    @app.route("/api/advisory", methods=["POST"])
    def get_advisory():
        try:
            return jsonify(advisory_service.predict_advisory(request.get_json() or {}))
        except Exception as exc:
            return jsonify({"advisory": "train_ok", "confidence": 50, "error": str(exc)}), 500

    @app.route("/api/stations")
    def get_stations():
        return jsonify(advisory_service.get_stations())

    @app.route("/api/bus-depots")
    def get_bus_depots():
        depots = bus_fare_calculator.get_all_depots()
        return jsonify({"success": True, "depots": depots, "count": len(depots)})

    @app.route("/api/nearest-depot")
    def get_nearest_depot():
        try:
            lat = float(request.args.get("lat"))
            lon = float(request.args.get("lon"))
            nearest = bus_fare_calculator.find_nearest_depot(lat, lon)
            if nearest:
                return jsonify({"success": True, "depot": nearest})
            return jsonify({"success": False, "error": "No depot found"}), 404
        except Exception as exc:
            return jsonify({"success": False, "error": str(exc)}), 500

    @app.route("/api/save-trip", methods=["POST"])
    @login_required
    def save_trip():
        try:
            save_trip_for_user(current_user, request.get_json() or {})
            return jsonify({"status": "ok", "message": "Trip saved successfully"})
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    @app.route("/api/current-aqi", methods=["GET"])
    def current_aqi():
        payload = get_current_aqi_snapshot()
        status_code = 200 if payload.get("status") == "success" else 500
        return jsonify(payload), status_code
