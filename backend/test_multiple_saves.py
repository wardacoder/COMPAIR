"""Test multiple saves of the same comparison."""
from database.connection import get_db_session
from database.models import Comparison
from database.repository import create_comparison
from datetime import datetime, timedelta
import uuid

print("=" * 60)
print("TESTING MULTIPLE SAVES OF SAME COMPARISON")
print("=" * 60)

test_items = ["Toyota Camry", "Toyota Corolla"]
test_category = "cars"
test_data = {"introduction": "Test", "table": []}

# Count existing
with get_db_session() as db:
    cutoff = datetime.utcnow() - timedelta(hours=1)
    existing = db.query(Comparison).filter(
        Comparison.items == test_items,
        Comparison.category == test_category,
        Comparison.created_at >= cutoff
    ).all()
    print(f"\nExisting comparisons with {test_items} in last hour: {len(existing)}")
    for i, comp in enumerate(existing, 1):
        print(f"  {i}. ID: {comp.comparison_id[:8]}..., Created: {comp.created_at}")

# Create 3 new comparisons (simulating 3 requests)
print("\n" + "=" * 60)
print("CREATING 3 NEW COMPARISONS")
print("=" * 60)

for i in range(3):
    comparison_id = str(uuid.uuid4())
    try:
        with get_db_session() as db:
            comp = create_comparison(
                db,
                comparison_id=comparison_id,
                user_id=None,
                original_comparison=test_data,
                items=test_items,
                category=test_category
            )
            print(f"✅ {i+1}. Created: {comparison_id[:8]}... at {comp.created_at}")
    except Exception as e:
        print(f"❌ {i+1}. Error: {e}")
        import traceback
        traceback.print_exc()

# Count after
print("\n" + "=" * 60)
print("CHECKING RESULTS")
print("=" * 60)

with get_db_session() as db:
    cutoff = datetime.utcnow() - timedelta(hours=1)
    after = db.query(Comparison).filter(
        Comparison.items == test_items,
        Comparison.category == test_category,
        Comparison.created_at >= cutoff
    ).all()
    print(f"\nTotal comparisons with {test_items} in last hour: {len(after)}")
    for i, comp in enumerate(after, 1):
        print(f"  {i}. ID: {comp.comparison_id[:8]}..., Created: {comp.created_at}")
    
    # Count pairs
    pair_counts = {}
    for comp in after:
        items_str = " vs ".join(sorted([str(i) for i in comp.items]))
        pair_counts[items_str] = pair_counts.get(items_str, 0) + 1
    
    print(f"\nPair count: {pair_counts.get('Camry vs Corolla', 0)} (should be {len(after)})")




