#!/usr/bin/env python3
"""
Simple PostgreSQL Database Viewer for Raahi (No external dependencies)
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

def view_users_simple(conn):
    """View users in simple format"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, is_admin, joined_date, 
                       location_enabled, co2_saved, money_saved, trips_taken
                FROM "user" 
                ORDER BY joined_date DESC
                LIMIT 10
            """)
            users = cur.fetchall()
            
            if not users:
                print("ℹ️ No users found in database")
                return
            
            print("\n👥 USERS (Last 10)")
            print("-" * 80)
            print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Admin':<7} {'Joined':<12} {'CO2 Saved':<12} {'Trips':<8}")
            print("-" * 80)
            
            for user in users:
                print(f"{user[0]:<5} {user[1]:<20} {user[2]:<25} {'Yes' if user[3] else 'No':<7} {user[4].strftime('%Y-%m-%d'):<12} {user[5]:>11.2f}kg {user[7]:<8}")
            
    except Exception as e:
        print(f"❌ Error viewing users: {e}")

def view_trips_simple(conn):
    """View trips in simple format"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, u.name as user_name, t.destination, t.mode, 
                       t.distance_km, t.co2_emitted, t.cost, t.timestamp
                FROM trip t
                JOIN "user" u ON t.user_id = u.id
                ORDER BY t.timestamp DESC
                LIMIT 20
            """)
            trips = cur.fetchall()
            
            if not trips:
                print("ℹ️ No trips found in database")
                return
            
            print("\n🚌 TRIPS (Last 20)")
            print("-" * 100)
            print(f"{'ID':<5} {'User':<15} {'Destination':<20} {'Mode':<10} {'Distance':<10} {'CO2':<8} {'Cost':<10} {'Date':<12}")
            print("-" * 100)
            
            for trip in trips:
                print(f"{trip[0]:<5} {trip[1]:<15} {trip[2]:<20} {trip[3]:<10} {trip[4]:>9.2f}km {trip[5]:>7.2f}kg ₹{trip[6]:>8.2f} {trip[7].strftime('%Y-%m-%d'):<12}")
            
    except Exception as e:
        print(f"❌ Error viewing trips: {e}")

def view_statistics_simple(conn):
    """View database statistics"""
    try:
        with conn.cursor() as cur:
            # User statistics
            cur.execute("SELECT COUNT(*) FROM \"user\"")
            total_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM \"user\" WHERE is_admin = TRUE")
            admin_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM trip")
            total_trips = cur.fetchone()[0]
            
            cur.execute("SELECT AVG(distance_km) FROM trip")
            avg_distance = cur.fetchone()[0]
            
            cur.execute("SELECT SUM(co2_emitted) FROM trip")
            total_co2 = cur.fetchone()[0]
            
            cur.execute("SELECT SUM(cost) FROM trip")
            total_cost = cur.fetchone()[0]
            
            print("\n📊 DATABASE STATISTICS")
            print("=" * 40)
            print(f"👥 Total Users: {total_users}")
            print(f"👑 Admin Users: {admin_users}")
            print(f"🚌 Total Trips: {total_trips}")
            print(f"📏 Average Distance: {avg_distance:.2f} km" if avg_distance else "N/A")
            print(f"🌱 Total CO2 Emitted: {total_co2:.2f} kg" if total_co2 else "N/A")
            print(f"💰 Total Cost: ₹{total_cost:.2f}" if total_cost else "N/A")
            
    except Exception as e:
        print(f"❌ Error viewing statistics: {e}")

def main():
    """Main database viewer function"""
    print("🐘 Simple Raahi PostgreSQL Database Viewer")
    print("=" * 50)
    
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        print("💡 Make sure PostgreSQL is running and .env file is correct")
        return
    
    try:
        while True:
            print("\n📋 MENU:")
            print("1. 👥 View Users (Last 10)")
            print("2. 🚌 View Trips (Last 20)")
            print("3. 📊 View Statistics")
            print("4. ❌ Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                view_users_simple(conn)
            elif choice == '2':
                view_trips_simple(conn)
            elif choice == '3':
                view_statistics_simple(conn)
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
