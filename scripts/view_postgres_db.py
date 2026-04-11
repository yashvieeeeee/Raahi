#!/usr/bin/env python3
"""
PostgreSQL Database Viewer for Raahi
View users, trips, and database statistics
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from tabulate import tabulate

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

def view_users(conn):
    """View all users"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, email, phone, is_admin, joined_date, 
                       location, location_enabled, co2_saved, money_saved, trips_taken
                FROM "user" 
                ORDER BY joined_date DESC
            """)
            users = cur.fetchall()
            
            if not users:
                print("ℹ️ No users found in database")
                return
            
            print("\n👥 USERS TABLE")
            print("=" * 80)
            
            # Format for display
            headers = ['ID', 'Name', 'Email', 'Phone', 'Admin', 'Joined', 'Location', 'Location Enabled', 'CO2 Saved', 'Money Saved', 'Trips']
            rows = []
            
            for user in users:
                rows.append([
                    user['id'],
                    user['name'],
                    user['email'],
                    user['phone'] or 'N/A',
                    'Yes' if user['is_admin'] else 'No',
                    user['joined_date'].strftime('%Y-%m-%d %H:%M'),
                    user['location'] or 'Not set',
                    'Yes' if user['location_enabled'] else 'No',
                    f"{user['co2_saved']:.2f} kg",
                    f"₹{user['money_saved']:.2f}",
                    user['trips_taken']
                ])
            
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            
    except Exception as e:
        print(f"❌ Error viewing users: {e}")

def view_trips(conn):
    """View all trips"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT t.id, u.name as user_name, t.destination, t.mode, 
                       t.distance_km, t.co2_emitted, t.cost, t.timestamp
                FROM trip t
                JOIN "user" u ON t.user_id = u.id
                ORDER BY t.timestamp DESC
                LIMIT 50
            """)
            trips = cur.fetchall()
            
            if not trips:
                print("ℹ️ No trips found in database")
                return
            
            print("\n🚌 TRIPS TABLE (Last 50)")
            print("=" * 100)
            
            # Format for display
            headers = ['ID', 'User', 'Destination', 'Mode', 'Distance (km)', 'CO2 (kg)', 'Cost (₹)', 'Date/Time']
            rows = []
            
            for trip in trips:
                rows.append([
                    trip['id'],
                    trip['user_name'],
                    trip['destination'],
                    trip['mode'],
                    f"{trip['distance_km']:.2f}",
                    f"{trip['co2_emitted']:.2f}",
                    f"₹{trip['cost']:.2f}",
                    trip['timestamp'].strftime('%Y-%m-%d %H:%M')
                ])
            
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            
    except Exception as e:
        print(f"❌ Error viewing trips: {e}")

def view_statistics(conn):
    """View database statistics"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # User statistics
            cur.execute("SELECT COUNT(*) as total_users FROM \"user\"")
            user_stats = cur.fetchone()
            
            cur.execute("SELECT COUNT(*) as admin_users FROM \"user\" WHERE is_admin = TRUE")
            admin_stats = cur.fetchone()
            
            cur.execute("SELECT COUNT(*) as location_enabled_users FROM \"user\" WHERE location_enabled = TRUE")
            location_stats = cur.fetchone()
            
            # Trip statistics
            cur.execute("SELECT COUNT(*) as total_trips FROM trip")
            trip_stats = cur.fetchone()
            
            cur.execute("SELECT AVG(distance_km) as avg_distance FROM trip")
            distance_stats = cur.fetchone()
            
            cur.execute("SELECT SUM(co2_emitted) as total_co2 FROM trip")
            co2_stats = cur.fetchone()
            
            cur.execute("SELECT SUM(cost) as total_cost FROM trip")
            cost_stats = cur.fetchone()
            
            print("\n📊 DATABASE STATISTICS")
            print("=" * 40)
            print(f"👥 Total Users: {user_stats['total_users']}")
            print(f"👑 Admin Users: {admin_stats['admin_users']}")
            print(f"📍 Location Enabled: {location_stats['location_enabled_users']}")
            print(f"🚌 Total Trips: {trip_stats['total_trips']}")
            print(f"📏 Average Distance: {distance_stats['avg_distance']:.2f} km")
            print(f"🌱 Total CO2 Emitted: {co2_stats['total_co2']:.2f} kg")
            print(f"💰 Total Cost: ₹{cost_stats['total_cost']:.2f}")
            
            # User with most trips
            cur.execute("""
                SELECT u.name, COUNT(t.id) as trip_count 
                FROM \"user\" u 
                LEFT JOIN trip t ON u.id = t.user_id 
                GROUP BY u.id, u.name 
                ORDER BY trip_count DESC 
                LIMIT 5
            """)
            top_users = cur.fetchall()
            
            print("\n🏆 TOP USERS BY TRIPS")
            for user in top_users:
                print(f"  {user['name']}: {user['trip_count']} trips")
            
    except Exception as e:
        print(f"❌ Error viewing statistics: {e}")

def search_users(conn, search_term):
    """Search users by name or email"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, email, joined_date, trips_taken, co2_saved
                FROM "user" 
                WHERE name ILIKE %s OR email ILIKE %s
                ORDER BY name
            """, (f'%{search_term}%', f'%{search_term}%'))
            
            users = cur.fetchall()
            
            if not users:
                print(f"ℹ️ No users found matching '{search_term}'")
                return
            
            print(f"\n🔍 SEARCH RESULTS FOR '{search_term}'")
            print("=" * 50)
            
            headers = ['ID', 'Name', 'Email', 'Joined', 'Trips', 'CO2 Saved']
            rows = []
            
            for user in users:
                rows.append([
                    user['id'],
                    user['name'],
                    user['email'],
                    user['joined_date'].strftime('%Y-%m-%d'),
                    user['trips_taken'],
                    f"{user['co2_saved']:.2f} kg"
                ])
            
            print(tabulate(rows, headers=headers, tablefmt='grid'))
            
    except Exception as e:
        print(f"❌ Error searching users: {e}")

def main():
    """Main database viewer function"""
    print("🐘 Raahi PostgreSQL Database Viewer")
    print("=" * 40)
    
    conn = get_connection()
    if not conn:
        print("❌ Cannot connect to database")
        print("💡 Make sure PostgreSQL is running and .env file is correct")
        return
    
    try:
        while True:
            print("\n📋 MENU OPTIONS:")
            print("1. 👥 View All Users")
            print("2. 🚌 View All Trips (Last 50)")
            print("3. 📊 View Statistics")
            print("4. 🔍 Search Users")
            print("5. ❌ Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                view_users(conn)
            elif choice == '2':
                view_trips(conn)
            elif choice == '3':
                view_statistics(conn)
            elif choice == '4':
                search_term = input("Enter search term (name/email): ").strip()
                if search_term:
                    search_users(conn, search_term)
            elif choice == '5':
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
