"""Test if cached comparisons are being saved."""
from database.connection import get_db_session
from database.models import Comparison
from database.repository import create_comparison
from datetime import datetime, timedelta
import uuid

print("=" * 60)
print("TESTING CACHED COMPARISON SAVE")
print("=" * 60)

# Test data
test_items = ["Test Item A", "Test Item B"]
test_category = "test"
test_data = {"test": "data"}

with get_db_session() as db:
    # Count before
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    before_count = db.query(Comparison).filter(
        Comparison.items == test_items,
        Comparison.created_at >= cutoff
    ).count()
    print(f"\nComparisons with {test_items} in last 5 minutes (before): {before_count}")
    
    # Create a comparison (simulating cached save)
    comparison_id = str(uuid.uuid4())
    try:
        comp = create_comparison(
            db,
            comparison_id=comparison_id,
            user_id=None,
            original_comparison=test_data,
            items=test_items,
            category=test_category
        )
        print(f"✅ Created comparison: {comparison_id[:8]}...")
        print(f"   Items: {comp.items}")
        print(f"   Created at: {comp.created_at}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Check after
with get_db_session() as db:
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    after_count = db.query(Comparison).filter(
        Comparison.items == test_items,
        Comparison.created_at >= cutoff
    ).count()
    print(f"\nComparisons with {test_items} in last 5 minutes (after): {after_count}")
    
    if after_count > before_count:
        print("✅ Save is working!")
    else:
        print("❌ Save might not be working - count didn't increase")




