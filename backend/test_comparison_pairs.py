"""Test script to check comparison pairs."""
from database.connection import get_db_session
from database.repository import get_comparison_pairs, get_dashboard_summary

print("=" * 60)
print("TESTING COMPARISON PAIRS")
print("=" * 60)

with get_db_session() as db:
    # Get comparison pairs
    pairs = get_comparison_pairs(db, days=30, limit=20)
    print(f"\nFound {len(pairs)} comparison pairs:")
    for p in pairs:
        print(f"  '{p['pair']}': {p['count']} times")
    
    # Get dashboard summary
    print("\n" + "=" * 60)
    print("DASHBOARD SUMMARY - most_compared_items")
    print("=" * 60)
    summary = get_dashboard_summary(db, days=30)
    most_compared = summary.get("most_compared_items", [])
    print(f"\nFound {len(most_compared)} items in most_compared_items:")
    for item in most_compared:
        print(f"  {item}")




