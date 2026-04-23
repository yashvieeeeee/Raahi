#!/usr/bin/env python3
"""
Fix PostgreSQL permissions for the configured application user.
"""

import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def fix_permissions():
    """Fix permissions for the configured PostgreSQL user."""
    admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "")
    if not admin_password or admin_password == "change-this-admin-password":
        print("Set a real POSTGRES_ADMIN_PASSWORD in .env before running this script.")
        return

    db_name = os.getenv("POSTGRES_DB", "raahi_db")
    db_user = os.getenv("POSTGRES_USER", "raahi_user")

    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=db_name,
            user=os.getenv("POSTGRES_ADMIN_USER", "postgres"),
            password=admin_password,
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("Fixing PostgreSQL permissions...")

        cur.execute(f"GRANT ALL ON SCHEMA public TO {db_user}")
        print("Granted schema permissions")

        cur.execute(f"GRANT ALL ON ALL TABLES IN SCHEMA public TO {db_user}")
        print("Granted table permissions")

        cur.execute(f"GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {db_user}")
        print("Granted sequence permissions")

        cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user}")
        print("Set default privileges")

        print("Permissions fixed successfully")
    except Exception as exc:
        print(f"Error fixing permissions: {exc}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    fix_permissions()
