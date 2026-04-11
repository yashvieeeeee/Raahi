#!/usr/bin/env python3
"""
Simple PostgreSQL Setup for Raahi - Try multiple authentication methods
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def try_postgres_connection():
    """Try different PostgreSQL connection methods"""
    connection_params = [
        # Try Windows authentication (no password)
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': ''
        },
        # Try common passwords
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'postgres'
        },
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': '123456'
        },
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'password'
        },
        # Try your custom password
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'xyz345'
        }
    ]
    
    for i, params in enumerate(connection_params, 1):
        try:
            conn = psycopg2.connect(**params)
            print(f"✅ Connected successfully with method {i}!")
            return conn, params
        except Exception as e:
            print(f"❌ Method {i} failed: {e}")
            continue
    
    return None, None

def create_database_and_user(conn, admin_params):
    """Create database and user"""
    try:
        conn.autocommit = True
        cur = conn.cursor()
        
        db_name = 'raahi_db'
        db_user = 'raahi_user'
        db_password = 'raahi_password'
        
        print(f"🐘 Creating database '{db_name}' and user '{db_user}'...")
        
        # Create database
        try:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️ Database '{db_name}' already exists")
        
        # Create user
        try:
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            print(f"✅ User '{db_user}' created")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️ User '{db_user}' already exists")
        
        # Grant privileges
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        print(f"✅ Privileges granted to '{db_user}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database/user: {e}")
        return False

def test_raahi_connection():
    """Test connection to Raahi database"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='raahi_db',
            user='raahi_user',
            password='raahi_password',
            port='5432'
        )
        print("✅ Raahi database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Raahi database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Simple PostgreSQL Setup for Raahi")
    print("=" * 40)
    
    # Try to connect with different methods
    conn, admin_params = try_postgres_connection()
    
    if not conn:
        print("\n❌ Could not connect to PostgreSQL with any method")
        print("\n💡 Please check:")
        print("1. PostgreSQL is running")
        print("2. Your PostgreSQL admin password")
        print("3. Try running: psql -U postgres")
        print("4. Or update POSTGRES_ADMIN_PASSWORD in .env file")
        sys.exit(1)
    
    try:
        # Create database and user
        if create_database_and_user(conn, admin_params):
            print("\n✅ Database setup completed!")
            
            # Test Raahi connection
            if test_raahi_connection():
                print("\n🎉 PostgreSQL is ready for Raahi!")
                print("\n📋 Next Steps:")
                print("1. Run migration: python migrate_to_postgres.py")
                print("2. Start application: python app_raahi.py")
            else:
                print("\n❌ Raahi database connection test failed")
        else:
            print("\n❌ Database setup failed")
            
    finally:
        conn.close()

if __name__ == "__main__":
    main()
