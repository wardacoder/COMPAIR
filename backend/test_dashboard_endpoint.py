"""
Quick test script to diagnose dashboard endpoint issues.
Run this to check if the dashboard endpoint is working.
"""

import requests
import sys

def test_dashboard_endpoint():
    """Test the dashboard endpoint."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Dashboard Endpoint Diagnostic Test")
    print("=" * 60)
    
    # Test 1: Check if backend is running
    print("\n1. Testing backend health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend!")
        print("   → Make sure backend is running: python main.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Check database health
    print("\n2. Testing database connection...")
    try:
        response = requests.get(f"{base_url}/health/db", timeout=5)
        if response.status_code == 200:
            print("   ✅ Database is connected")
            db_info = response.json()
            print(f"   Pool size: {db_info.get('pool_size', 'N/A')}")
            print(f"   Checked in connections: {db_info.get('checked_in_connections', 'N/A')}")
        else:
            print(f"   ⚠️  Database health check returned status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ⚠️  Database health check error: {e}")
    
    # Test 3: Test dashboard endpoint
    print("\n3. Testing dashboard endpoint...")
    try:
        response = requests.get(f"{base_url}/analytics/dashboard?days=30", timeout=10)
        if response.status_code == 200:
            print("   ✅ Dashboard endpoint is working!")
            data = response.json()
            print(f"   Total comparisons: {data.get('total_comparisons', 0)}")
            print(f"   Categories: {len(data.get('category_stats', []))}")
            print(f"   Feedback stats available: {bool(data.get('feedback_stats'))}")
            return True
        else:
            print(f"   ❌ Dashboard endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (database query taking too long)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\nMake sure backend is running: python main.py\n")
    success = test_dashboard_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Dashboard should work.")
    else:
        print("❌ Tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Start backend: python main.py")
        print("2. Initialize database: python -c \"from database.init_db import init_db; init_db()\"")
        print("3. Check DATABASE_URL environment variable")
    print("=" * 60)
    
    sys.exit(0 if success else 1)




