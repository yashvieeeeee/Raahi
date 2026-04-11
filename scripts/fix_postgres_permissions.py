#!/usr/bin/env python3
"""
Fix PostgreSQL permissions for Raahi user
"""

import psycopg2

def fix_permissions():
    """Fix permissions for raahi_user"""
    try:
        # Connect as admin
        conn = psycopg2.connect(
            host='localhost',
            database='raahi_db',
            user='postgres',
            password='xyz345',
            port='5432'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🔧 Fixing PostgreSQL permissions...")
        
        # Grant schema permissions
        cur.execute('GRANT ALL ON SCHEMA public TO raahi_user')
        print("✅ Granted schema permissions")
        
        # Grant table permissions
        cur.execute('GRANT ALL ON ALL TABLES IN SCHEMA public TO raahi_user')
        print("✅ Granted table permissions")
        
        # Grant sequence permissions
        cur.execute('GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO raahi_user')
        print("✅ Granted sequence permissions")
        
        # Set default permissions for future tables
        cur.execute('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO raahi_user')
        print("✅ Set default privileges")
        
        print("🎉 Permissions fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_permissions()
