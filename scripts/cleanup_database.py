#!/usr/bin/env python3
"""
Clean up the Raahi database while preserving protected accounts.
"""

import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """Connect to the PostgreSQL database."""
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


def cleanup_database():
    """Delete all users except protected accounts."""
    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            admin_email = os.getenv("ADMIN_EMAIL", "admin@raahi.local")
            protected_email = os.getenv("PROTECTED_EMAIL", "")
            protected_emails = [admin_email]
            if protected_email:
                protected_emails.append(protected_email)

            print("\nRAAHI DATABASE CLEANUP")
            print("=" * 60)
            print("Protected users:")
            for email in protected_emails:
                print(f"  - {email}")
            print("=" * 60)

            cur.execute('SELECT COUNT(*) FROM "user"')
            total_users = cur.fetchone()[0]
            print(f"\nCurrent users: {total_users}")

            where_clause = " OR ".join(["email = %s"] * len(protected_emails))
            cur.execute(f'SELECT id FROM "user" WHERE {where_clause}', protected_emails)
            protected_ids = [row[0] for row in cur.fetchall()]
            print(f"Protected user IDs: {protected_ids}")

            if not protected_ids:
                print("\nNo protected users found. Aborting for safety.")
                return

            placeholders = ",".join(["%s"] * len(protected_ids))
            cur.execute(
                f'SELECT id, name, email FROM "user" WHERE id NOT IN ({placeholders})',
                protected_ids,
            )
            users_to_delete = cur.fetchall()

            if not users_to_delete:
                print("\nNo users to delete. Database is already clean.")
                return

            print(f"\nUsers to delete ({len(users_to_delete)}):")
            for user_id, name, email in users_to_delete:
                print(f"  - {user_id}: {name} ({email})")

            confirmation = input("\nType 'yes' to confirm deletion: ")
            if confirmation.lower() != "yes":
                print("Deletion cancelled.")
                return

            user_ids_to_delete = [user[0] for user in users_to_delete]
            delete_placeholders = ",".join(["%s"] * len(user_ids_to_delete))

            cur.execute(
                f"DELETE FROM trip WHERE user_id IN ({delete_placeholders})",
                user_ids_to_delete,
            )
            trips_deleted = cur.rowcount
            print(f"\nDeleted {trips_deleted} trips")

            cur.execute(
                f'DELETE FROM "user" WHERE id IN ({delete_placeholders})',
                user_ids_to_delete,
            )
            users_deleted = cur.rowcount
            print(f"Deleted {users_deleted} users")

            conn.commit()

            cur.execute('SELECT COUNT(*) FROM "user"')
            remaining_users = cur.fetchone()[0]
            print("\n" + "=" * 60)
            print("CLEANUP COMPLETE")
            print("=" * 60)
            print(f"Remaining users: {remaining_users}")
    except Exception as exc:
        conn.rollback()
        print(f"\nError during cleanup: {exc}")
    finally:
        conn.close()


if __name__ == "__main__":
    cleanup_database()
