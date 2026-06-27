"""Test the actual /compare API endpoint to see if saves work."""
import requests
import json
import time

API_URL = "http://localhost:8000/compare"

test_data = {
    "category": "cars",
    "items": ["Test Car A", "Test Car B"]
}

print("=" * 60)
print("TESTING /compare API ENDPOINT")
print("=" * 60)

# Make 3 identical requests
for i in range(3):
    print(f"\n{i+1}. Making comparison request...")
    try:
        response = requests.post(API_URL, json=test_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            comp_id = data.get("comparison_id", "N/A")
            print(f"   ✅ Success! Comparison ID: {comp_id[:8]}...")
            print(f"   Items: {data.get('items', [])}")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Small delay between requests
    if i < 2:
        time.sleep(1)

print("\n" + "=" * 60)
print("Now check the database to see if all 3 were saved!")
print("=" * 60)




