#!/usr/bin/env python3
"""
Clean up orphaned trip records (trips with non-existent user_id).
This fixes data inconsistencies when users are deleted.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.extensions import db
from backend.database.models import Trip, User
from backend.main import create_app

def cleanup_orphaned_trips():
    """Remove trips with non-existent user_id."""
    app = create_app()
    
    with app.app_context():
        # Get all trips
        all_trips = Trip.query.all()
        
        # Find trips with user_id not in user table
        user_ids = set(user.id for user in User.query.all())
        orphaned_trips = [trip for trip in all_trips if trip.user_id not in user_ids]
        
        if not orphaned_trips:
            print("✓ No orphaned trips found. Database is clean.")
            return
        
        print(f"\n⚠ Found {len(orphaned_trips)} orphaned trips:")
        for trip in orphaned_trips:
            print(f"  - Trip ID: {trip.id}, User ID: {trip.user_id} (deleted)")
        
        # Ask for confirmation
        confirm = input(f"\nDelete these {len(orphaned_trips)} orphaned trips? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("❌ Cleanup cancelled.")
            return
        
        # Delete orphaned trips
        for trip in orphaned_trips:
            db.session.delete(trip)
        
        db.session.commit()
        print(f"\n✓ Successfully deleted {len(orphaned_trips)} orphaned trips.")
        print("✓ Database is now clean and consistent.")

if __name__ == "__main__":
    cleanup_orphaned_trips()
