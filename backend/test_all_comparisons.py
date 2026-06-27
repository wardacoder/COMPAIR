"""Test all comparisons to see pair counts."""
from database.connection import get_db_session
from database.models import Comparison
from datetime import datetime, timedelta

cutoff = datetime.utcnow() - timedelta(days=30)

with get_db_session() as db:
    comparisons = db.query(Comparison).filter(Comparison.created_at >= cutoff).all()
    
    print(f"Total comparisons: {len(comparisons)}")
    print("\nAll comparisons:")
    for i, comp in enumerate(comparisons, 1):
        items = comp.items if isinstance(comp.items, list) else []
        print(f"{i}. {items} - Created: {comp.created_at}")
    
    # Count pairs
    pair_counts = {}
    for comp in comparisons:
        items = comp.items if isinstance(comp.items, list) else []
        if len(items) >= 2:
            sorted_items = sorted([str(item).strip() for item in items])
            pair_key = " vs ".join(sorted_items)
            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
    
    print("\n" + "=" * 60)
    print("PAIR COUNTS:")
    print("=" * 60)
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
    for pair, count in sorted_pairs:
        print(f"  {pair}: {count} times")
    
    # Show pairs with count >= 3
    print("\n" + "=" * 60)
    print("PAIRS WITH COUNT >= 3:")
    print("=" * 60)
    pairs_3plus = [(p, c) for p, c in sorted_pairs if c >= 3]
    if pairs_3plus:
        for pair, count in pairs_3plus:
            print(f"  {pair}: {count} times")
    else:
        print("  None found - all pairs have count <= 2")




