from datetime import datetime

from flask_login import UserMixin

from backend.database.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)
    location_enabled = db.Column(db.Boolean, default=False, nullable=False)
    co2_saved = db.Column(db.Float, default=0.0)
    money_saved = db.Column(db.Float, default=0.0)
    trips_taken = db.Column(db.Integer, default=0)

    # Cascade delete ensures trips are deleted when user is deleted
    trips = db.relationship("Trip", backref="user", lazy=True, cascade="all, delete-orphan")


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    co2_emitted = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
