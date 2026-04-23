#!/usr/bin/env python3
"""
Simple PostgreSQL setup for Raahi using environment variables.
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def try_postgres_connection():
    """Try connecting with the configured admin credentials."""
    admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "")
    if not admin_password or admin_password == "change-this-admin-password":
        print("Set a real POSTGRES_ADMIN_PASSWORD in .env before running this script.")
        return None

    params = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "database": "postgres",
        "user": os.getenv("POSTGRES_ADMIN_USER", "postgres"),
        "password": admin_password,
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }

    try:
        conn = psycopg2.connect(**params)
        print("Connected successfully with configured admin credentials.")
        return conn
    except Exception as exc:
        print(f"Connection failed: {exc}")
        return None


def create_database_and_user(conn):
    """Create database and user."""
    try:
        conn.autocommit = True
        cur = conn.cursor()

        db_name = os.getenv("POSTGRES_DB", "raahi_db")
        db_user = os.getenv("POSTGRES_USER", "raahi_user")
        db_password = os.getenv("POSTGRES_PASSWORD", "")
        if not db_password or db_password == "change-this-database-password":
            raise RuntimeError("Set a real POSTGRES_PASSWORD in .env before running setup.")

        print(f"Creating database '{db_name}' and user '{db_user}'...")

        try:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{db_name}' already exists")

        try:
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            print(f"User '{db_user}' created")
        except psycopg2.errors.DuplicateObject:
            print(f"User '{db_user}' already exists")

        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        print(f"Privileges granted to '{db_user}'")
        return True
    except Exception as exc:
        print(f"Error creating database/user: {exc}")
        return False


def test_raahi_connection():
    """Test connection to the configured Raahi database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "raahi_db"),
            user=os.getenv("POSTGRES_USER", "raahi_user"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        print("Raahi database connection successful")
        conn.close()
        return True
    except Exception as exc:
        print(f"Raahi database connection failed: {exc}")
        return False


def main():
    """Main setup function."""
    print("Simple PostgreSQL Setup for Raahi")
    print("=" * 40)

    conn = try_postgres_connection()
    if not conn:
        print("\nCould not connect to PostgreSQL with the configured credentials.")
        print("Check .env and confirm PostgreSQL is running.")
        sys.exit(1)

    try:
        if create_database_and_user(conn):
            print("\nDatabase setup completed.")
            if test_raahi_connection():
                print("\nPostgreSQL is ready for Raahi.")
                print("\nNext steps:")
                print("1. Run migration: python scripts/migrate_to_postgres.py")
                print("2. Start application: python -m backend.main")
            else:
                print("\nRaahi database connection test failed.")
        else:
            print("\nDatabase setup failed.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
