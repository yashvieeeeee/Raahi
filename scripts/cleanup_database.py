#!/usr/bin/env python3
"""
Clean up Raahi database - delete all users except admin and a specific email
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'raahi_db'),
            user=os.getenv('POSTGRES_USER', 'raahi_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'raahi_password'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        return None


def cleanup_database():
    """Delete all users except admin and yashviemahey1@gmail.com"""
    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Protected emails
            ADMIN_EMAIL = "admin@raahi.com"
            PROTECTED_EMAIL = "yashviemahey1@gmail.com"
            
            print("\n🗑️  RAAHI DATABASE CLEANUP")
            print("=" * 60)
            print(f"Protected users:")
            print(f"  ✓ {ADMIN_EMAIL} (Admin)")
            print(f"  ✓ {PROTECTED_EMAIL}")
            print("=" * 60)

            # Get current user count
            cur.execute('SELECT COUNT(*) FROM "user"')
            total_users = cur.fetchone()[0]
            print(f"\n📊 Current users: {total_users}")

            # Get protected user IDs
            cur.execute(
                'SELECT id FROM "user" WHERE email = %s OR email = %s',
                (ADMIN_EMAIL, PROTECTED_EMAIL)
            )
            protected_ids = [row[0] for row in cur.fetchall()]
            print(f"Protected user IDs: {protected_ids}")

            # Get users to delete
            placeholders = ','.join(['%s'] * len(protected_ids))
            cur.execute(
                f'SELECT id, name, email FROM "user" WHERE id NOT IN ({placeholders})',
                protected_ids
            )
            users_to_delete = cur.fetchall()
            
            if not users_to_delete:
                print("\n✅ No users to delete. Database is already clean!")
                conn.close()
                return

            print(f"\n🔍 Users to delete ({len(users_to_delete)}):")
            for user_id, name, email in users_to_delete:
                print(f"  - {name} ({email})")

            # Confirm deletion
            confirmation = input("\n⚠️  Are you sure you want to delete these users? Type 'yes' to confirm: ")
            if confirmation.lower() != 'yes':
                print("❌ Deletion cancelled.")
                conn.close()
                return

            # Delete trips for users to be deleted
            user_ids_to_delete = [user[0] for user in users_to_delete]
            placeholders = ','.join(['%s'] * len(user_ids_to_delete))
            
            cur.execute(
                f'DELETE FROM trip WHERE user_id IN ({placeholders})',
                user_ids_to_delete
            )
            trips_deleted = cur.rowcount
            print(f"\n🗑️  Deleted {trips_deleted} trips")

            # Delete users
            cur.execute(
                f'DELETE FROM "user" WHERE id IN ({placeholders})',
                user_ids_to_delete
            )
            users_deleted = cur.rowcount
            print(f"🗑️  Deleted {users_deleted} users")

            # Commit changes
            conn.commit()

            # Final count
            cur.execute('SELECT COUNT(*) FROM "user"')
            remaining_users = cur.fetchone()[0]
            
            print("\n" + "=" * 60)
            print("✅ CLEANUP COMPLETE!")
            print("=" * 60)
            print(f"Remaining users: {remaining_users}")
            cur.execute('SELECT id, name, email, is_admin FROM "user" ORDER BY id')
            for user_id, name, email, is_admin in cur.fetchall():
                admin_badge = " 👑 ADMIN" if is_admin else ""
                print(f"  [{user_id}] {name} ({email}){admin_badge}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during cleanup: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    cleanup_database()