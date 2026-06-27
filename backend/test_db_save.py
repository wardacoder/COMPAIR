"""Test script to diagnose database save issues."""
import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_session, init_db
from database.repository import create_comparison, get_comparison
from database.models import Comparison

def test_db_save():
    """Test if database saves are working."""
    print("=" * 60)
    print("DATABASE SAVE TEST")
    print("=" * 60)
    
    # Check database connection
    try:
        print("\n1. Testing database connection...")
        with get_db_session() as db:
            print("   ✅ Database connection successful")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # Test creating a comparison
    try:
        print("\n2. Testing comparison creation...")
        comparison_id = str(uuid.uuid4())
        test_data = {
            "introduction": "Test comparison",
            "table": [{"feature": "Test", "Item1": "Value1", "Item2": "Value2"}],
            "pros": ["Item1: Test pro"],
            "cons": ["Item1: Test con"]
        }
        
        with get_db_session() as db:
            comparison = create_comparison(
                db,
                comparison_id=comparison_id,
                user_id=None,
                original_comparison=test_data,
                items=["Item1", "Item2"],
                category="test"
            )
            print(f"   ✅ Comparison created: {comparison.comparison_id}")
        
        # Verify it was saved
        print("\n3. Verifying comparison was saved...")
        with get_db_session() as db:
            saved_comparison = get_comparison(db, comparison_id)
            if saved_comparison:
                print(f"   ✅ Comparison found in database!")
                print(f"   ✅ ID: {saved_comparison.comparison_id}")
                print(f"   ✅ Category: {saved_comparison.category}")
                print(f"   ✅ Items: {saved_comparison.items}")
                print(f"   ✅ Created at: {saved_comparison.created_at}")
                return True
            else:
                print(f"   ❌ Comparison NOT found in database!")
                return False
                
    except Exception as e:
        print(f"   ❌ Error creating comparison: {e}")
        import traceback
        print(f"   ❌ Traceback: {traceback.format_exc()}")
        return False

def check_recent_comparisons():
    """Check recent comparisons in database."""
    print("\n" + "=" * 60)
    print("RECENT COMPARISONS CHECK")
    print("=" * 60)
    
    try:
        with get_db_session() as db:
            recent = db.query(Comparison).order_by(Comparison.created_at.desc()).limit(5).all()
            print(f"\nFound {len(recent)} recent comparisons:")
            for comp in recent:
                print(f"  - ID: {comp.comparison_id}")
                print(f"    Category: {comp.category}")
                print(f"    Items: {comp.items}")
                print(f"    Created: {comp.created_at}")
                print()
    except Exception as e:
        print(f"❌ Error checking recent comparisons: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    print("\n🔍 Running database diagnostics...\n")
    
    # Check if database is initialized
    try:
        init_db()
        print("✅ Database initialized\n")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}\n")
    
    # Run tests
    success = test_db_save()
    
    # Check recent comparisons
    check_recent_comparisons()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed - check errors above")




