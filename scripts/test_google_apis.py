#!/usr/bin/env python3
"""
Google APIs Integration Status and Testing Script
Tests all Google Maps services with your API key
"""

import requests
import json

API_KEY = "AIzaSyBZrGSUuzA_dD8-nMgyn7QKwnzVc4oZ6Y8"

def test_places_api():
    """Test Google Places API"""
    print("🗺️ Testing Google Places API...")
    
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJd3aQ6X5lsReR7kA6ThAGv&fields=name,formatted_address,geometry&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Places API working: {data['result']['name']}")
            print(f"📍 Address: {data['result']['formatted_address']}")
            print(f"🌍 Coordinates: {data['result']['geometry']['location']}")
            return True
        else:
            print(f"❌ Places API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Places API error: {e}")
        return False

def test_geocoding_api():
    """Test Google Geocoding API"""
    print("\n🌍 Testing Google Geocoding API...")
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Bandra%20Station,%20Mumbai&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                location = data['results'][0]['geometry']['location']
                print(f"✅ Geocoding API working")
                print(f"📍 Bandra Station: {location['lat']}, {location['lng']}")
                return True
        else:
            print("❌ No results found")
            return False
    except Exception as e:
        print(f"❌ Geocoding API error: {e}")
        return False

def test_directions_api():
    """Test Google Directions API"""
    print("\n🛣️ Testing Google Directions API...")
    
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin=19.0760,72.8777&destination=19.0549,72.8464&mode=driving&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['routes']:
                route = data['routes'][0]
                distance = route['legs'][0]['distance']['text']
                duration = route['legs'][0]['duration']['text']
                print(f"✅ Directions API working")
                print(f"🚗 Distance: {distance}")
                print(f"⏱️ Duration: {duration}")
                return True
        else:
            print("❌ No routes found")
            return False
    except Exception as e:
        print(f"❌ Directions API error: {e}")
        return False

def test_static_maps_api():
    """Test Google Static Maps API"""
    print("\n🗺️ Testing Google Static Maps API...")
    
    url = f"https://maps.googleapis.com/maps/api/staticmap?center=19.0760,72.8777&zoom=15&size=600x400&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Static Maps API working: {response.status_code}")
            print("📊 Static map generated successfully")
            return True
        else:
            print(f"❌ Static Maps API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Static Maps API error: {e}")
        return False

def test_street_view_api():
    """Test Google Street View API"""
    print("\n🏠️ Testing Google Street View API...")
    
    url = f"https://maps.googleapis.com/maps/api/streetview?location=19.0760,72.8777&heading=0&pitch=0&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Street View API working: {response.status_code}")
            print("🏠️ Street view available")
            return True
        else:
            print(f"❌ Street View API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Street View API error: {e}")
        return False

def test_elevation_api():
    """Test Google Elevation API"""
    print("\n⛰️ Testing Google Elevation API...")
    
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations=19.0760,72.8777&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                elevation = data['results'][0]['elevation']
                print(f"✅ Elevation API working: {elevation}m")
                return True
        else:
            print("❌ No elevation data")
            return False
    except Exception as e:
        print(f"❌ Elevation API error: {e}")
        return False

def main():
    """Main testing function"""
    print("🔑 Google APIs Integration Test")
    print("=" * 50)
    print(f"🔑 Using API Key: {API_KEY}")
    print(f"🌍 APIs to Test:")
    print("  🗺️ Places API - Location search and details")
    print("  🌍 Geocoding API - Address to coordinates")
    print("  🛣️ Directions API - Route planning")
    print("  🗺️ Static Maps API - Map images")
    print("  🏠️ Street View API - 360° views")
    print("  ⛰️ Elevation API - Altitude data")
    
    # Test all APIs
    results = []
    results.append(test_places_api())
    results.append(test_geocoding_api())
    results.append(test_directions_api())
    results.append(test_static_maps_api())
    results.append(test_street_view_api())
    results.append(test_elevation_api())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results:")
    print(f"  ✅ Passed: {passed}/{total}")
    print(f"  ❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Google APIs working perfectly!")
        print("🚀 Your Raahi application is ready with full Google Maps integration!")
    else:
        print("\n⚠️ Some APIs may need attention")
        print("💡 Check API key quotas and permissions")
    
    print(f"\n🔗 API Documentation: https://developers.google.com/maps/documentation")
    print(f"🔑 API Console: https://console.cloud.google.com/apis/dashboard")

if __name__ == "__main__":
    main()
