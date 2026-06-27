"""Test the actual API response."""
import requests
import json

try:
    r = requests.get('http://localhost:8000/analytics/dashboard?days=30', timeout=5)
    if r.status_code == 200:
        data = r.json()
        print("=" * 60)
        print("API RESPONSE CHECK")
        print("=" * 60)
        print(f"\ncomparison_pairs count: {len(data.get('comparison_pairs', []))}")
        print(f"most_compared_items count: {len(data.get('most_compared_items', []))}")
        
        print("\ncomparison_pairs (first 20):")
        pairs = data.get('comparison_pairs', [])
        for i, p in enumerate(pairs[:20], 1):
            print(f"  {i}. {p.get('pair', 'N/A')}: {p.get('count', 0)}x")
        
        print("\nmost_compared_items (first 20):")
        items = data.get('most_compared_items', [])
        for i, item in enumerate(items[:20], 1):
            print(f"  {i}. {item.get('name', 'N/A')}: {item.get('count', 0)}x")
        
        # Check for pairs with count >= 3
        print("\n" + "=" * 60)
        print("PAIRS WITH COUNT >= 3:")
        print("=" * 60)
        pairs_3plus = [p for p in pairs if p.get('count', 0) >= 3]
        if pairs_3plus:
            for p in pairs_3plus:
                print(f"  {p.get('pair')}: {p.get('count')}x")
        else:
            print("  None found")
    else:
        print(f"API Error: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"Error: {e}")




