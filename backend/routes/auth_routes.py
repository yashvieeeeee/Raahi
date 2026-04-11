from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user

from backend.services.auth_service import authenticate_user, register_user


def register_auth_routes(app):
    @app.route("/")
    def index():
        return render_template("welcome.html")

    @app.route("/auth")
    def auth():
        initial_user_view = request.args.get("view", "login")

        if initial_user_view not in {"login", "register"}:
            initial_user_view = "login"

        return render_template(
            "auth.html",
            initial_user_view=initial_user_view,
        )

    @app.route("/auth/register", methods=["POST"])
    def register():
        name = request.form.get("name")
        email_or_phone = request.form.get("email_or_phone")
        password = request.form.get("password")

        if not name or not email_or_phone or not password:
            flash("All fields are required")
            return redirect(url_for("auth", view="register"))

        user, error = register_user(name, email_or_phone, password)
        if error:
            flash(error)
            return redirect(url_for("auth", view="register"))

        login_user(user)
        return redirect(url_for("location_permission"))

    @app.route("/auth/login", methods=["POST"])
    def login():
        email_or_phone = request.form.get("email_or_phone")
        password = request.form.get("password")

        if not email_or_phone or not password:
            flash("Email/phone and password required")
            return redirect(url_for("auth", view="login"))

        user = authenticate_user(email_or_phone, password)
        if user is None:
            flash("Invalid credentials")
            return redirect(url_for("auth", view="login"))

        login_user(user)
        session["is_admin"] = user.is_admin
        return redirect(url_for("admin_dashboard" if user.is_admin else "home"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for("index"))
