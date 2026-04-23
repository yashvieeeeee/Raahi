#!/usr/bin/env python3
"""
PostgreSQL database viewer for Raahi.
"""

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from tabulate import tabulate


load_dotenv()


def get_connection():
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
        print(f"Cannot connect to database: {exc}")
        return None


def view_users(conn):
    """View all users."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, is_admin, joined_date,
                       location, location_enabled, co2_saved, money_saved, trips_taken
                FROM "user"
                ORDER BY joined_date DESC
                """
            )
            users = cur.fetchall()

            if not users:
                print("No users found in database")
                return

            headers = [
                "ID",
                "Name",
                "Email",
                "Phone",
                "Admin",
                "Joined",
                "Location",
                "Location Enabled",
                "CO2 Saved",
                "Money Saved",
                "Trips",
            ]
            rows = []
            for user in users:
                rows.append(
                    [
                        user["id"],
                        user["name"],
                        user["email"],
                        user["phone"] or "N/A",
                        "Yes" if user["is_admin"] else "No",
                        user["joined_date"].strftime("%Y-%m-%d %H:%M"),
                        user["location"] or "Not set",
                        "Yes" if user["location_enabled"] else "No",
                        f"{user['co2_saved']:.2f} kg",
                        f"Rs.{user['money_saved']:.2f}",
                        user["trips_taken"],
                    ]
                )

            print("\nUSERS TABLE")
            print("=" * 80)
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as exc:
        print(f"Error viewing users: {exc}")


def view_trips(conn):
    """View all trips."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT t.id, u.name AS user_name, t.destination, t.mode,
                       t.distance_km, t.co2_emitted, t.cost, t.timestamp
                FROM trip t
                JOIN "user" u ON t.user_id = u.id
                ORDER BY t.timestamp DESC
                LIMIT 50
                """
            )
            trips = cur.fetchall()

            if not trips:
                print("No trips found in database")
                return

            headers = [
                "ID",
                "User",
                "Destination",
                "Mode",
                "Distance (km)",
                "CO2 (kg)",
                "Cost (Rs.)",
                "Date/Time",
            ]
            rows = []
            for trip in trips:
                rows.append(
                    [
                        trip["id"],
                        trip["user_name"],
                        trip["destination"],
                        trip["mode"],
                        f"{trip['distance_km']:.2f}",
                        f"{trip['co2_emitted']:.2f}",
                        f"Rs.{trip['cost']:.2f}",
                        trip["timestamp"].strftime("%Y-%m-%d %H:%M"),
                    ]
                )

            print("\nTRIPS TABLE (Last 50)")
            print("=" * 100)
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as exc:
        print(f"Error viewing trips: {exc}")


def view_statistics(conn):
    """View database statistics."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT COUNT(*) AS total_users FROM "user"')
            user_stats = cur.fetchone()

            cur.execute('SELECT COUNT(*) AS admin_users FROM "user" WHERE is_admin = TRUE')
            admin_stats = cur.fetchone()

            cur.execute('SELECT COUNT(*) AS location_enabled_users FROM "user" WHERE location_enabled = TRUE')
            location_stats = cur.fetchone()

            cur.execute("SELECT COUNT(*) AS total_trips FROM trip")
            trip_stats = cur.fetchone()

            cur.execute("SELECT AVG(distance_km) AS avg_distance FROM trip")
            distance_stats = cur.fetchone()

            cur.execute("SELECT SUM(co2_emitted) AS total_co2 FROM trip")
            co2_stats = cur.fetchone()

            cur.execute("SELECT SUM(cost) AS total_cost FROM trip")
            cost_stats = cur.fetchone()

            print("\nDATABASE STATISTICS")
            print("=" * 40)
            print(f"Total Users: {user_stats['total_users']}")
            print(f"Admin Users: {admin_stats['admin_users']}")
            print(f"Location Enabled: {location_stats['location_enabled_users']}")
            print(f"Total Trips: {trip_stats['total_trips']}")
            print(f"Average Distance: {distance_stats['avg_distance']:.2f} km")
            print(f"Total CO2 Emitted: {co2_stats['total_co2']:.2f} kg")
            print(f"Total Cost: Rs.{cost_stats['total_cost']:.2f}")
    except Exception as exc:
        print(f"Error viewing statistics: {exc}")


def search_users(conn, search_term):
    """Search users by name or email."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, email, joined_date, trips_taken, co2_saved
                FROM "user"
                WHERE name ILIKE %s OR email ILIKE %s
                ORDER BY name
                """,
                (f"%{search_term}%", f"%{search_term}%"),
            )

            users = cur.fetchall()
            if not users:
                print(f"No users found matching '{search_term}'")
                return

            headers = ["ID", "Name", "Email", "Joined", "Trips", "CO2 Saved"]
            rows = []
            for user in users:
                rows.append(
                    [
                        user["id"],
                        user["name"],
                        user["email"],
                        user["joined_date"].strftime("%Y-%m-%d"),
                        user["trips_taken"],
                        f"{user['co2_saved']:.2f} kg",
                    ]
                )

            print(f"\nSEARCH RESULTS FOR '{search_term}'")
            print("=" * 50)
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Exception as exc:
        print(f"Error searching users: {exc}")


def main():
    """Main database viewer function."""
    print("Raahi PostgreSQL Database Viewer")
    print("=" * 40)

    conn = get_connection()
    if not conn:
        print("Cannot connect to database")
        print("Make sure PostgreSQL is running and .env is configured")
        return

    try:
        while True:
            print("\nMENU OPTIONS:")
            print("1. View All Users")
            print("2. View All Trips (Last 50)")
            print("3. View Statistics")
            print("4. Search Users")
            print("5. Exit")

            choice = input("\nEnter your choice (1-5): ").strip()
            if choice == "1":
                view_users(conn)
            elif choice == "2":
                view_trips(conn)
            elif choice == "3":
                view_statistics(conn)
            elif choice == "4":
                search_term = input("Enter search term (name/email): ").strip()
                if search_term:
                    search_users(conn, search_term)
            elif choice == "5":
                print("Goodbye")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nGoodbye")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
