"""Test dashboard endpoint to find the exact error."""
from database.connection import get_db_session
from database.repository import get_dashboard_summary

try:
    print("Testing dashboard summary...")
    with get_db_session() as db:
        result = get_dashboard_summary(db, days=30)
        print("✅ Success!")
        print(f"Total comparisons: {result.get('total_comparisons', 0)}")
        print(f"Keys: {list(result.keys())}")
        print(f"Comparison pairs: {len(result.get('comparison_pairs', []))}")
        print(f"Category stats: {len(result.get('category_stats', []))}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

