#!/usr/bin/env python3
"""
Delete a specific user from Raahi database
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


def delete_user(email):
    """Delete a specific user by email"""
    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute('SELECT id, email FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()
            
            if not user:
                print(f"❌ User with email '{email}' not found")
                conn.close()
                return
            
            user_id, user_email = user
            print(f"\n🗑️  DELETING USER")
            print("=" * 60)
            print(f"Email: {user_email}")
            print(f"ID: {user_id}")
            print("=" * 60)
            
            # Confirm deletion
            confirm = input("\nAre you sure? Type 'yes' to confirm: ").strip().lower()
            if confirm != 'yes':
                print("❌ Cancelled")
                conn.close()
                return
            
            # Delete user's trips first (foreign key constraint)
            cur.execute('DELETE FROM trip WHERE user_id = %s', (user_id,))
            trips_deleted = cur.rowcount
            
            # Delete user
            cur.execute('DELETE FROM "user" WHERE id = %s', (user_id,))
            users_deleted = cur.rowcount
            
            conn.commit()
            
            print(f"\n✅ User deleted successfully!")
            print(f"  - Trips deleted: {trips_deleted}")
            print(f"  - Users deleted: {users_deleted}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    email = input("Enter email to delete: ").strip()
    if email:
        delete_user(email)
    else:
        print("❌ No email provided")
