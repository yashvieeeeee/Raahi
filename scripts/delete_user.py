#!/usr/bin/env python3
"""
Delete a specific user from the Raahi database.
"""

import os

import psycopg2
from dotenv import load_dotenv


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


def delete_user(email):
    """Delete a specific user by email."""
    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, email FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()

            if not user:
                print(f"User with email '{email}' not found")
                return

            user_id, user_email = user
            print("\nDELETING USER")
            print("=" * 60)
            print(f"Email: {user_email}")
            print(f"ID: {user_id}")
            print("=" * 60)

            confirm = input("\nAre you sure? Type 'yes' to confirm: ").strip().lower()
            if confirm != "yes":
                print("Cancelled")
                return

            cur.execute("DELETE FROM trip WHERE user_id = %s", (user_id,))
            trips_deleted = cur.rowcount

            cur.execute('DELETE FROM "user" WHERE id = %s', (user_id,))
            users_deleted = cur.rowcount

            conn.commit()

            print("\nUser deleted successfully")
            print(f"Trips deleted: {trips_deleted}")
            print(f"Users deleted: {users_deleted}")
    except Exception as exc:
        print(f"Error: {exc}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    email = input("Enter email to delete: ").strip()
    if email:
        delete_user(email)
    else:
        print("No email provided")
