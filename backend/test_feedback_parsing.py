"""
Test the feedback parsing function to see what it returns.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_session
from database.repository import get_feedback_stats

def test_feedback_parsing():
    """Test what get_feedback_stats returns."""
    with get_db_session() as db:
        stats = get_feedback_stats(db, days=30)
        print("Feedback Stats Returned:")
        print(json.dumps(stats, indent=2))
        print("\n")
        print(f"Liked comments count: {len(stats.get('liked_comments', []))}")
        print(f"Improvement comments count: {len(stats.get('improvement_comments', []))}")
        print("\nLiked comments:")
        for i, comment in enumerate(stats.get('liked_comments', []), 1):
            print(f"  {i}. {comment}")
        print("\nImprovement comments:")
        for i, comment in enumerate(stats.get('improvement_comments', []), 1):
            print(f"  {i}. {comment}")

if __name__ == "__main__":
    test_feedback_parsing()






