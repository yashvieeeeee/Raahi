#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL.
"""

import os
import sqlite3
import sys

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_sqlite_connection():
    """Connect to SQLite database."""
    try:
        conn = sqlite3.connect("raahi.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as exc:
        print(f"Error connecting to SQLite: {exc}")
        return None


def get_postgres_connection():
    """Connect to PostgreSQL database."""
    try:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "raahi_db"),
            user=os.getenv("POSTGRES_USER", "raahi_user"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
    except Exception as exc:
        print(f"Error connecting to PostgreSQL: {exc}")
        return None


def create_postgres_tables(pg_conn):
    """Create tables in PostgreSQL."""
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) UNIQUE,
        phone VARCHAR(20),
        password_hash VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        location VARCHAR(100),
        location_enabled BOOLEAN DEFAULT FALSE NOT NULL,
        co2_saved FLOAT DEFAULT 0.0,
        money_saved FLOAT DEFAULT 0.0,
        trips_taken INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS trip (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        destination VARCHAR(200) NOT NULL,
        mode VARCHAR(50) NOT NULL,
        distance_km FLOAT NOT NULL,
        co2_emitted FLOAT NOT NULL,
        cost FLOAT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
    CREATE INDEX IF NOT EXISTS idx_trip_user_id ON trip(user_id);
    CREATE INDEX IF NOT EXISTS idx_trip_timestamp ON trip(timestamp);
    """

    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(create_tables_sql)
        pg_conn.commit()
        print("PostgreSQL tables created successfully")
        return True
    except Exception as exc:
        print(f"Error creating PostgreSQL tables: {exc}")
        return False


def migrate_users(sqlite_conn, pg_conn):
    """Migrate users from SQLite to PostgreSQL."""
    try:
        sqlite_cur = sqlite_conn.cursor()
        pg_cur = pg_conn.cursor()
        sqlite_cur.execute("SELECT * FROM user")
        users = sqlite_cur.fetchall()

        if not users:
            print("No users found in SQLite database")
            return True

        for user in users:
            pg_cur.execute(
                """
                INSERT INTO "user" (
                    name, email, phone, password_hash, is_admin, joined_date,
                    location, location_enabled, co2_saved, money_saved, trips_taken
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user["name"],
                    user["email"],
                    user["phone"],
                    user["password_hash"],
                    user["is_admin"],
                    user["joined_date"],
                    user["location"],
                    user["location_enabled"],
                    user["co2_saved"],
                    user["money_saved"],
                    user["trips_taken"],
                ),
            )

        pg_conn.commit()
        print(f"Migrated {len(users)} users to PostgreSQL")
        return True
    except Exception as exc:
        print(f"Error migrating users: {exc}")
        pg_conn.rollback()
        return False


def migrate_trips(sqlite_conn, pg_conn):
    """Migrate trips from SQLite to PostgreSQL."""
    try:
        sqlite_cur = sqlite_conn.cursor()
        pg_cur = pg_conn.cursor()
        sqlite_cur.execute("SELECT * FROM trip")
        trips = sqlite_cur.fetchall()

        if not trips:
            print("No trips found in SQLite database")
            return True

        for trip in trips:
            pg_cur.execute(
                """
                INSERT INTO trip (user_id, destination, mode, distance_km, co2_emitted, cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    trip["user_id"],
                    trip["destination"],
                    trip["mode"],
                    trip["distance_km"],
                    trip["co2_emitted"],
                    trip["cost"],
                    trip["timestamp"],
                ),
            )

        pg_conn.commit()
        print(f"Migrated {len(trips)} trips to PostgreSQL")
        return True
    except Exception as exc:
        print(f"Error migrating trips: {exc}")
        pg_conn.rollback()
        return False


def main():
    """Main migration function."""
    print("Starting SQLite to PostgreSQL migration...")

    sqlite_conn = get_sqlite_connection()
    if not sqlite_conn:
        print("Cannot connect to SQLite database")
        sys.exit(1)

    pg_conn = get_postgres_connection()
    if not pg_conn:
        print("Cannot connect to PostgreSQL database")
        print("Make sure PostgreSQL is running and environment variables are set:")
        print("  POSTGRES_HOST=localhost")
        print("  POSTGRES_DB=your_database_name")
        print("  POSTGRES_USER=your_database_user")
        print("  POSTGRES_PASSWORD=your_real_database_password")
        print("  POSTGRES_PORT=5432")
        sqlite_conn.close()
        sys.exit(1)

    try:
        if not create_postgres_tables(pg_conn):
            sys.exit(1)
        if not migrate_users(sqlite_conn, pg_conn):
            sys.exit(1)
        if not migrate_trips(sqlite_conn, pg_conn):
            sys.exit(1)

        print("Migration completed successfully")
        print("You can now use PostgreSQL with your Raahi application")
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
