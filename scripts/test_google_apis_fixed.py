#!/usr/bin/env python3
"""
Simple Google API Key Test
"""

import requests

API_KEY = "AIzaSyBZrGSUuzA_dD8-nMgyn7QKwnzVc4oZ6Y8"

def test_api_key():
    """Test if Google API key is working"""
    print("🔑 Testing Google API Key...")
    print(f"🔑 Key: {API_KEY}")
    
    # Test Places API
    try:
        url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input=Mumbai&types=establishment&key={API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Places API: Working")
            print(f"📍 Mumbai locations found: {len(response.json().get('predictions', []))}")
        else:
            print(f"❌ Places API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test Geocoding API
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Bandra%20Station&key={API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                location = data['results'][0]['geometry']['location']
                print("✅ Geocoding API: Working")
                print(f"📍 Bandra Station: {location['lat']}, {location['lng']}")
        else:
            print("❌ Geocoding API: No results")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test Directions API
    try:
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin=19.0760,72.8777&destination=19.0549,72.8464&mode=driving&key={API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('routes'):
                route = data['routes'][0]
                print("✅ Directions API: Working")
                print(f"🚗 Route distance: {route['legs'][0]['distance']['text']}")
        else:
            print("❌ Directions API: No routes")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_key()
