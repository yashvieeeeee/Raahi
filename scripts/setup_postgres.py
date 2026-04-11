#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Raahi Application
This script sets up PostgreSQL database and user
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def create_database_and_user():
    """Create PostgreSQL database and user"""
    try:
        # Connect to PostgreSQL default database (usually postgres)
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database='postgres',
            user=os.getenv('POSTGRES_ADMIN_USER', 'postgres'),
            password=os.getenv('POSTGRES_ADMIN_PASSWORD', ''),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Database configuration
        db_name = os.getenv('POSTGRES_DB', 'raahi_db')
        db_user = os.getenv('POSTGRES_USER', 'raahi_user')
        db_password = os.getenv('POSTGRES_PASSWORD', 'raahi_password')
        
        print(f"🐘 Setting up PostgreSQL for Raahi...")
        print(f"📊 Database: {db_name}")
        print(f"👤 User: {db_user}")
        
        # Create database if it doesn't exist
        try:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️ Database '{db_name}' already exists")
        
        # Create user if it doesn't exist
        try:
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            print(f"✅ User '{db_user}' created")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️ User '{db_user}' already exists")
        
        # Grant privileges
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        print(f"✅ Privileges granted to '{db_user}'")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up PostgreSQL: {e}")
        return False

def test_connection():
    """Test connection to the new database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'raahi_db'),
            user=os.getenv('POSTGRES_USER', 'raahi_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'raahi_password'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL connection successful!")
        print(f"📊 Version: {version.split(',')[0]}")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_env_file():
    """Create .env file with PostgreSQL configuration"""
    env_content = """# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_DB=raahi_db
POSTGRES_USER=raahi_user
POSTGRES_PASSWORD=raahi_password
POSTGRES_PORT=5432

# PostgreSQL Admin (for setup)
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=

# Flask Configuration
SECRET_KEY=raahi-secret-key-fallback-2024
SQLITE_DATABASE_URI=sqlite:///raahi.db
DATABASE_URL=postgresql://raahi_user:raahi_password@localhost:5432/raahi_db
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created with PostgreSQL configuration")
    else:
        print("ℹ️ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Raahi PostgreSQL Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    print("\n📋 Setup Instructions:")
    print("1. Make sure PostgreSQL is installed and running")
    print("2. Set POSTGRES_ADMIN_PASSWORD in .env file (your PostgreSQL admin password)")
    print("3. Run this script again to create database and user")
    print("4. Run migration script: python migrate_to_postgres.py")
    
    # Check if admin password is set
    admin_password = os.getenv('POSTGRES_ADMIN_PASSWORD')
    if not admin_password or admin_password == '':
        print("\n⚠️ Please set POSTGRES_ADMIN_PASSWORD in .env file first")
        print("   This is your PostgreSQL admin password (usually 'postgres' or empty)")
        return
    
    # Create database and user
    if create_database_and_user():
        print("\n✅ PostgreSQL setup completed!")
        
        # Test connection
        if test_connection():
            print("\n🎉 PostgreSQL is ready for Raahi!")
            print("\n📋 Next Steps:")
            print("1. Install requirements: pip install -r requirements.txt")
            print("2. Run migration: python migrate_to_postgres.py")
            print("3. Start application: python app_raahi.py")
        else:
            print("\n❌ Connection test failed")
    else:
        print("\n❌ PostgreSQL setup failed")

if __name__ == "__main__":
    main()
