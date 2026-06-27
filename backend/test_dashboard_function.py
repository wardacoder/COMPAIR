"""Test dashboard function directly."""
from database.connection import get_db_session
from database.repository import get_dashboard_summary, get_comparison_pairs

print("=" * 60)
print("TESTING DASHBOARD FUNCTION")
print("=" * 60)

with get_db_session() as db:
    # Test get_comparison_pairs directly
    print("\n1. Testing get_comparison_pairs with limit=50:")
    pairs = get_comparison_pairs(db, days=30, limit=50)
    print(f"   Returned {len(pairs)} pairs")
    for i, p in enumerate(pairs[:20], 1):
        print(f"   {i}. {p['pair']}: {p['count']}x")
    
    # Test get_dashboard_summary
    print("\n2. Testing get_dashboard_summary:")
    summary = get_dashboard_summary(db, days=30)
    cp = summary.get('comparison_pairs', [])
    mci = summary.get('most_compared_items', [])
    print(f"   comparison_pairs: {len(cp)} items")
    print(f"   most_compared_items: {len(mci)} items")
    
    print("\n   comparison_pairs (first 20):")
    for i, p in enumerate(cp[:20], 1):
        print(f"   {i}. {p.get('pair', 'N/A')}: {p.get('count', 0)}x")
    
    print("\n   most_compared_items (first 10):")
    for i, item in enumerate(mci[:10], 1):
        print(f"   {i}. {item.get('name', 'N/A')}: {item.get('count', 0)}x")




