import subprocess

from flask import Response, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from backend.database.extensions import db
from backend.database.models import Trip, User
from backend.services.admin_service import (
    export_analytics_payload,
    export_users_payload,
    get_admin_dashboard_context,
    model_validation_payload,
    refresh_model_metrics,
    retrain_model_metrics,
    test_prediction_payload,
)
from backend.utils.paths import PROJECT_ROOT


def register_admin_routes(app):
    def _render_pdf_report(report_type: str, filename: str):
        cli_path = PROJECT_ROOT / "backend" / "pdf_export_service" / "src" / "renderReportCli.js"
        try:
            completed = subprocess.run(
                ["node", str(cli_path), report_type],
                cwd=PROJECT_ROOT,
                capture_output=True,
                timeout=180,
                check=False,
            )
        except FileNotFoundError:
            return jsonify({"error": "Node.js is not installed on this system."}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"error": "PDF generation timed out."}), 504

        if completed.returncode != 0:
            error_message = completed.stderr.decode("utf-8", errors="replace").strip() or "PDF generation failed."
            return jsonify({"error": error_message}), 500

        pdf_bytes = completed.stdout
        if not pdf_bytes.startswith(b"%PDF"):
            return jsonify({"error": "Generated file is not a valid PDF."}), 500

        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    @app.route("/admin-dashboard")
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return redirect(url_for("profile"))
        return render_template("admin.html", **get_admin_dashboard_context())

    @app.route("/retrain-model", methods=["POST"])
    @login_required
    def retrain_model():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        metrics = retrain_model_metrics()
        if metrics:
            return jsonify(
                {
                    "success": True,
                    "message": "Model retrained successfully",
                    "accuracy": metrics.get("accuracy", 0),
                    "precision": metrics.get("precision", 0),
                    "recall": metrics.get("recall", 0),
                    "f1_score": metrics.get("f1_score", 0),
                }
            )
        return jsonify({"error": "Model retraining failed"}), 500

    @app.route("/update-model-metrics", methods=["POST"])
    @login_required
    def update_model_metrics():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        metrics = refresh_model_metrics()
        if metrics:
            return jsonify({"success": True, "message": "Metrics updated successfully", "metrics": metrics})
        return jsonify({"error": "Failed to update metrics"}), 500

    @app.route("/export-analytics")
    @login_required
    def export_analytics():
        if not current_user.is_admin:
            return redirect(url_for("profile"))
        return jsonify(export_analytics_payload())

    @app.route("/export-users")
    @login_required
    def export_users():
        if not current_user.is_admin:
            return redirect(url_for("profile"))
        return jsonify(export_users_payload())

    @app.route("/api/export-analytics")
    @login_required
    def export_analytics_pdf():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return _render_pdf_report("analytics", "raahi-analytics-report.pdf")

    @app.route("/api/export-users")
    @login_required
    def export_users_pdf():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return _render_pdf_report("users", "raahi-users-report.pdf")

    @app.route("/api/admin/model-validation")
    @login_required
    def get_model_validation():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return jsonify(model_validation_payload())

    @app.route("/api/admin/model-predict-test", methods=["POST"])
    @login_required
    def test_model_prediction():
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        features = (request.get_json() or {}).get("features", [])
        return jsonify(test_prediction_payload(features))

    @app.route("/api/admin/cleanup-orphaned-trips", methods=["POST"])
    @login_required
    def cleanup_orphaned_trips():
        """Clean up orphaned trip records (trips with deleted users)."""
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        try:
            # Get all trips with non-existent user_id
            all_trips = Trip.query.all()
            user_ids = set(user.id for user in User.query.all())
            orphaned_trips = [trip for trip in all_trips if trip.user_id not in user_ids]

            if not orphaned_trips:
                return jsonify({
                    "success": True,
                    "message": "No orphaned trips found",
                    "cleaned_count": 0
                })

            # Delete orphaned trips
            with db.session.begin_nested():
                for trip in orphaned_trips:
                    db.session.delete(trip)
                db.session.commit()

            return jsonify({
                "success": True,
                "message": f"Successfully deleted {len(orphaned_trips)} orphaned trips",
                "cleaned_count": len(orphaned_trips)
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500
