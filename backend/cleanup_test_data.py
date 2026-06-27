"""
Cleanup script to remove test data from the database.

This script removes all comparisons, cache entries, items, and feedback
with category="test" that were created during development/testing.

Usage:
    python cleanup_test_data.py
"""

import logging
from database.connection import get_db_session
from database.models import Comparison, ComparisonCache, Item, Feedback, SharedComparison
from sqlalchemy import and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_test_data():
    """Remove all test data from the database."""
    try:
        with get_db_session() as db:
            # Count test data before deletion
            test_comparisons_count = db.query(Comparison).filter(Comparison.category == "test").count()
            test_cache_count = db.query(ComparisonCache).filter(ComparisonCache.category == "test").count()
            test_items_count = db.query(Item).filter(Item.category == "test").count()
            test_shared_count = db.query(SharedComparison).filter(SharedComparison.category == "test").count()
            
            # Get comparison IDs for test comparisons to delete related feedback
            test_comparison_ids = [
                comp.comparison_id 
                for comp in db.query(Comparison.comparison_id)
                .filter(Comparison.category == "test")
                .all()
            ]
            test_feedback_count = db.query(Feedback).filter(
                Feedback.comparison_id.in_(test_comparison_ids)
            ).count() if test_comparison_ids else 0
            
            logger.info("=" * 60)
            logger.info("CLEANUP TEST DATA")
            logger.info("=" * 60)
            logger.info(f"Found test data:")
            logger.info(f"  - Comparisons: {test_comparisons_count}")
            logger.info(f"  - Cache entries: {test_cache_count}")
            logger.info(f"  - Items: {test_items_count}")
            logger.info(f"  - Shared comparisons: {test_shared_count}")
            logger.info(f"  - Feedback entries: {test_feedback_count}")
            logger.info("=" * 60)
            
            if (test_comparisons_count == 0 and test_cache_count == 0 and 
                test_items_count == 0 and test_shared_count == 0 and test_feedback_count == 0):
                logger.info("✅ No test data found. Database is clean!")
                return
            
            # Delete feedback first (foreign key dependency)
            if test_feedback_count > 0:
                deleted_feedback = db.query(Feedback).filter(
                    Feedback.comparison_id.in_(test_comparison_ids)
                ).delete(synchronize_session=False)
                logger.info(f"✅ Deleted {deleted_feedback} feedback entries")
            
            # Delete shared comparisons
            if test_shared_count > 0:
                deleted_shared = db.query(SharedComparison).filter(
                    SharedComparison.category == "test"
                ).delete(synchronize_session=False)
                logger.info(f"✅ Deleted {deleted_shared} shared comparisons")
            
            # Delete comparisons
            if test_comparisons_count > 0:
                deleted_comparisons = db.query(Comparison).filter(
                    Comparison.category == "test"
                ).delete(synchronize_session=False)
                logger.info(f"✅ Deleted {deleted_comparisons} comparisons")
            
            # Delete cache entries
            if test_cache_count > 0:
                deleted_cache = db.query(ComparisonCache).filter(
                    ComparisonCache.category == "test"
                ).delete(synchronize_session=False)
                logger.info(f"✅ Deleted {deleted_cache} cache entries")
            
            # Delete items
            if test_items_count > 0:
                deleted_items = db.query(Item).filter(
                    Item.category == "test"
                ).delete(synchronize_session=False)
                logger.info(f"✅ Deleted {deleted_items} items")
            
            # Commit all deletions
            db.commit()
            
            logger.info("=" * 60)
            logger.info("✅ Cleanup completed successfully!")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete all data with category='test'")
    print("This includes comparisons, cache entries, items, shared comparisons, and feedback.")
    response = input("\nDo you want to proceed? (yes/no): ")
    
    if response.lower() in ["yes", "y"]:
        cleanup_test_data()
    else:
        print("Cleanup cancelled.")




