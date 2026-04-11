#!/usr/bin/env python3
"""
Delete all trip records created by admin users.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.extensions import db
from backend.database.models import Trip, User
from backend.main import create_app

def delete_admin_trips():
    """Remove all trips created by admin users."""
    app = create_app()
    
    with app.app_context():
        # Get all admin users
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("✓ No admin users found.")
            return
        
        admin_ids = [admin.id for admin in admin_users]
        
        # Find trips by admin users
        admin_trips = Trip.query.filter(Trip.user_id.in_(admin_ids)).all()
        
        if not admin_trips:
            print("✓ No trips found from admin users. Database is clean.")
            return
        
        print(f"\n⚠ Found {len(admin_trips)} trips by admin users:")
        for admin in admin_users:
            trips_by_admin = [t for t in admin_trips if t.user_id == admin.id]
            if trips_by_admin:
                print(f"  - Admin '{admin.name}' ({admin.email}): {len(trips_by_admin)} trips")
        
        # Ask for confirmation
        confirm = input(f"\nDelete these {len(admin_trips)} admin trips? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("❌ Deletion cancelled.")
            return
        
        # Delete admin trips
        for trip in admin_trips:
            db.session.delete(trip)
        
        db.session.commit()
        print(f"\n✓ Successfully deleted {len(admin_trips)} admin trips.")
        print("✓ Admin trip logs have been cleared.")

if __name__ == "__main__":
    delete_admin_trips()
