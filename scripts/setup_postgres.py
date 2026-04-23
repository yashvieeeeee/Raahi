#!/usr/bin/env python3
"""
PostgreSQL setup script for Raahi.
Creates a database and user using values from the environment.
"""

import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def create_database_and_user():
    """Create the PostgreSQL database and user."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database="postgres",
            user=os.getenv("POSTGRES_ADMIN_USER", "postgres"),
            password=os.getenv("POSTGRES_ADMIN_PASSWORD", ""),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        conn.autocommit = True
        cur = conn.cursor()

        db_name = os.getenv("POSTGRES_DB", "raahi_db")
        db_user = os.getenv("POSTGRES_USER", "raahi_user")
        db_password = os.getenv("POSTGRES_PASSWORD", "")

        if not db_password:
            raise RuntimeError("POSTGRES_PASSWORD must be set before running setup.")

        print("Setting up PostgreSQL for Raahi...")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")

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

        conn.close()
        return True
    except Exception as exc:
        print(f"Error setting up PostgreSQL: {exc}")
        return False


def test_connection():
    """Test connection to the configured database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "raahi_db"),
            user=os.getenv("POSTGRES_USER", "raahi_user"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print("PostgreSQL connection successful")
        print(f"Version: {version.split(',')[0]}")
        conn.close()
        return True
    except Exception as exc:
        print(f"Connection test failed: {exc}")
        return False


def create_env_file():
    """Create a starter .env file when one does not exist."""
    env_content = """# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=change-this-database-password
POSTGRES_PORT=5432

# PostgreSQL Admin (for setup)
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=change-this-admin-password

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
SQLITE_DATABASE_URI=sqlite:///raahi.db
DATABASE_URL=postgresql://your_database_user:change-this-database-password@localhost:5432/your_database_name
"""

    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as file:
            file.write(env_content)
        print(".env file created with placeholder PostgreSQL configuration")
    else:
        print(".env file already exists")


def main():
    """Main setup flow."""
    print("Raahi PostgreSQL Setup")
    print("=" * 40)

    create_env_file()

    print("\nSetup instructions:")
    print("1. Make sure PostgreSQL is installed and running")
    print("2. Update POSTGRES_ADMIN_PASSWORD in .env")
    print("3. Update POSTGRES_PASSWORD in .env")
    print("4. Run this script again to create the database and user")

    admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "")
    db_password = os.getenv("POSTGRES_PASSWORD", "")

    if not admin_password or admin_password == "change-this-admin-password":
        print("\nPlease set a real POSTGRES_ADMIN_PASSWORD in .env first.")
        return

    if not db_password or db_password == "change-this-database-password":
        print("\nPlease set a real POSTGRES_PASSWORD in .env first.")
        return

    if create_database_and_user():
        print("\nPostgreSQL setup completed.")
        if test_connection():
            print("\nNext steps:")
            print("1. Install requirements: pip install -r requirements.txt")
            print("2. Run migration: python scripts/migrate_to_postgres.py")
            print("3. Start application: python -m backend.main")
        else:
            print("\nConnection test failed.")
    else:
        print("\nPostgreSQL setup failed.")


if __name__ == "__main__":
    main()
