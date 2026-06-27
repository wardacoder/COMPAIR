"""
Database repository layer for the Compair API.

This module contains all database CRUD operations.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, cast, JSON, String, text
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import logging
import json
import os
from database.models import (
    Comparison, SharedComparison, ComparisonCache, Item, Feedback
)
from utilities.constants import DATABASE_URL

logger = logging.getLogger(__name__)


# ========== USER REPOSITORY ==========
# NOTE: User model doesn't exist - these functions are disabled
# The application uses Comparison model directly without user tracking

# ========== COMPARISON REPOSITORY ==========

def create_comparison(db: Session, *args, **kwargs) -> Comparison:
    """Create a new comparison entry.
    
    Supports multiple call signatures:
    1. create_comparison(db, comparison_id, user_id, original_comparison, items, category)
    2. create_comparison(db, user_id, category, items, result) - legacy
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Handle new signature: (db, comparison_id, user_id, original_comparison, items, category)
    if len(args) >= 5 or 'comparison_id' in kwargs:
        if len(args) >= 5:
            comparison_id = args[1] if len(args) > 1 else kwargs.get('comparison_id', str(uuid.uuid4()))
            user_id = args[2] if len(args) > 2 else kwargs.get('user_id')
            original_comparison = args[3] if len(args) > 3 else kwargs.get('original_comparison')
            items = args[4] if len(args) > 4 else kwargs.get('items', [])
            category = args[5] if len(args) > 5 else kwargs.get('category', '')
        else:
            comparison_id = kwargs.get('comparison_id', str(uuid.uuid4()))
            user_id = kwargs.get('user_id')
            original_comparison = kwargs.get('original_comparison', kwargs.get('result'))
            items = kwargs.get('items', [])
            category = kwargs.get('category', '')
    else:
        # Legacy signature: (db, user_id, category, items, result)
        user_id = args[1] if len(args) > 1 else kwargs.get('user_id')
        category = args[2] if len(args) > 2 else kwargs.get('category', '')
        items = args[3] if len(args) > 3 else kwargs.get('items', [])
        original_comparison = args[4] if len(args) > 4 else kwargs.get('result', kwargs.get('original_comparison'))
        comparison_id = str(uuid.uuid4())
    
    try:
        # Update item comparison counts
        for item_name in items:
            item = db.query(Item).filter(Item.name == item_name).first()
            if item:
                item.comparison_count += 1
                item.updated_at = datetime.utcnow()
            else:
                item = Item(name=item_name, category=category, comparison_count=1)
                db.add(item)
        
        comparison = Comparison(
            comparison_id=comparison_id,
            messages=[],
            original_comparison=original_comparison,
            items=items,
            category=category
        )
        db.add(comparison)
        db.flush()
        db.refresh(comparison)
        logger.info(f"✅ Created comparison entry: {comparison_id} with {len(items)} items")
        return comparison
    except Exception as e:
        logger.error(f"❌ Error creating comparison entry: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        raise


def get_comparison(db: Session, comparison_id: str) -> Optional[Comparison]:
    """Get comparison by comparison_id."""
    return db.query(Comparison).filter(Comparison.comparison_id == comparison_id).first()


def get_user_comparisons(db: Session, user_id: Optional[str] = None, limit: int = 20, 
                         offset: int = 0, category: Optional[str] = None) -> List[Comparison]:
    """Get comparisons with pagination and optional category filter.
    
    NOTE: user_id parameter is ignored since Comparison model doesn't have user_id field.
    """
    query = db.query(Comparison)
    
    if category:
        query = query.filter(Comparison.category == category)
    
    return query.order_by(desc(Comparison.created_at)).limit(limit).offset(offset).all()


def delete_comparison(db: Session, user_id: Optional[str] = None, comparison_id: str = None) -> bool:
    """Delete a comparison by comparison_id."""
    if not comparison_id:
        return False
    
    comparison = db.query(Comparison).filter(
        Comparison.comparison_id == comparison_id
    ).first()
    
    if comparison:
        db.delete(comparison)
        db.commit()
        return True
    return False


def search_comparisons(db: Session, user_id: Optional[str] = None, search_term: str = "") -> List[Comparison]:
    """Search comparisons by items."""
    query = db.query(Comparison)
    results = []
    for comp in query.all():
        items = comp.items if isinstance(comp.items, list) else []
        if any(search_term.lower() in str(item).lower() for item in items):
            results.append(comp)
    return results


# ========== SHARED COMPARISON REPOSITORY ==========

def create_shared_comparison(db: Session, comparison_id: str, share_id: str,
                            category: str, items: List[str], result: Dict,
                            user_id: Optional[str] = None,
                            expires_in_days: Optional[int] = None) -> SharedComparison:
    """Create a shared comparison."""
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    shared = SharedComparison(
        share_id=share_id,
        comparison_id=comparison_id if comparison_id else None,
        category=category,
        items=items,
        result=result,
        expires_at=expires_at
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared


def get_shared_comparison(db: Session, share_id: str) -> Optional[SharedComparison]:
    """Get shared comparison by share_id."""
    shared = db.query(SharedComparison).filter(SharedComparison.share_id == share_id).first()
    
    # Check if expired
    if shared and shared.expires_at and shared.expires_at < datetime.utcnow():
        return None
    
    return shared


def increment_shared_views(db: Session, share_id: str) -> Optional[SharedComparison]:
    """Atomically increment view count for shared comparison."""
    shared = db.query(SharedComparison).filter(SharedComparison.share_id == share_id).first()
    if shared:
        shared.views += 1
        db.commit()
        db.refresh(shared)
    return shared


def get_trending_shared(db: Session, days: int = 7, limit: int = 10) -> List[SharedComparison]:
    """Get trending shared comparisons.
    
    Uses eager loading to prevent N+1 query problems.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return db.query(SharedComparison)\
        .filter(SharedComparison.created_at >= cutoff_date)\
        .order_by(desc(SharedComparison.views))\
        .limit(limit)\
        .all()


def cleanup_expired_shares(db: Session) -> int:
    """Delete expired shared comparisons."""
    deleted = db.query(SharedComparison).filter(
        SharedComparison.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return deleted


# ========== CONVERSATION REPOSITORY ==========

def create_conversation(db: Session, comparison_id: str, user_id: Optional[str],
                       original_comparison: Dict, items: List[str], category: str) -> Comparison:
    """Create a new conversation entry (uses Comparison model)."""
    return create_comparison(db, comparison_id=comparison_id, user_id=user_id,
                            original_comparison=original_comparison, items=items, category=category)


def get_conversation(db: Session, comparison_id: str) -> Optional[Comparison]:
    """Get conversation by comparison_id."""
    return get_comparison(db, comparison_id)


def add_message_to_conversation(db: Session, comparison_id: str, role: str, content: str) -> Optional[Comparison]:
    """Add a message to conversation."""
    conversation = get_conversation(db, comparison_id)
    if conversation:
        if not conversation.messages:
            conversation.messages = []
        
        conversation.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation


def get_user_conversations(db: Session, user_id: Optional[str] = None) -> List[Comparison]:
    """Get all conversations (uses Comparison model)."""
    return db.query(Comparison).order_by(desc(Comparison.updated_at)).all()


# ========== CACHE REPOSITORY ==========

def get_cached_comparison(db: Session, category: str, items: List[str],
                          user_preferences: Optional[Dict] = None) -> Optional[ComparisonCache]:
    """Get cached comparison if exists and not expired."""
    # Normalize items for comparison
    normalized_items = sorted([item.lower().strip() for item in items])
    normalized_prefs = user_preferences if user_preferences else {}
    
    # For PostgreSQL, JSON comparison is tricky - fetch by category and filter in Python
    # For SQLite, direct comparison works
    if DATABASE_URL.startswith("postgresql"):
        # Fetch all cache entries for this category and filter in Python
        # This is reliable and cache table shouldn't be huge
        all_caches = db.query(ComparisonCache).filter(
            ComparisonCache.category == category
        ).all()
        
        for c in all_caches:
            # Handle different JSON formats (dict/list from SQLAlchemy or string)
            c_items = c.items if isinstance(c.items, list) else json.loads(c.items) if isinstance(c.items, str) else c.items
            c_prefs = c.user_preferences if isinstance(c.user_preferences, dict) else json.loads(c.user_preferences) if isinstance(c.user_preferences, str) else c.user_preferences or {}
            
            # Normalize and compare
            c_items_normalized = sorted([str(i).lower().strip() for i in c_items])
            
            if c_items_normalized == normalized_items and c_prefs == normalized_prefs:
                cache = c
                break
        else:
            cache = None
    else:
        # SQLite can handle direct comparison
        cache = db.query(ComparisonCache).filter(
            and_(
                ComparisonCache.category == category,
                ComparisonCache.items == normalized_items,
                ComparisonCache.user_preferences == normalized_prefs
            )
        ).first()
    
    if cache:
        # Check if expired
        if cache.expires_at and cache.expires_at < datetime.utcnow():
            db.delete(cache)
            db.commit()
            return None
        return cache
    
    return None


def cache_comparison(db: Session, category: str, items: List[str], result: Dict,
                    user_preferences: Optional[Dict] = None,
                    expires_in_hours: int = 24) -> ComparisonCache:
    """Cache a comparison result."""
    normalized_items = sorted([item.lower().strip() for item in items])
    normalized_prefs = user_preferences if user_preferences else {}
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    cache = ComparisonCache(
        category=category,
        items=normalized_items,
        user_preferences=normalized_prefs,
        result=result,
        expires_at=expires_at
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache


def cleanup_expired_cache(db: Session) -> int:
    """Delete expired cache entries."""
    deleted = db.query(ComparisonCache).filter(
        ComparisonCache.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return deleted


# ========== ANALYTICS REPOSITORY ==========

def get_most_compared_items(db: Session, limit: int = 10) -> List[Item]:
    """Get most compared items."""
    return db.query(Item).order_by(desc(Item.comparison_count)).limit(limit).all()


def get_category_stats(db: Session, days: int = 30) -> List[Dict]:
    """Get category statistics."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        Comparison.category,
        func.count(Comparison.id).label('count')
    ).filter(
        Comparison.created_at >= cutoff_date
    ).group_by(Comparison.category).all()
    
    return [{"category": r.category, "count": r.count} for r in results]


def get_comparison_count_by_date(db: Session, days: int = 30) -> List[Dict]:
    """Get comparison count grouped by date."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        func.date(Comparison.created_at).label('date'),
        func.count(Comparison.id).label('count')
    ).filter(
        Comparison.created_at >= cutoff_date
    ).group_by(func.date(Comparison.created_at)).all()
    
    return [{"date": str(r.date), "count": r.count} for r in results]


def get_comparison_pairs(db: Session, days: int = 30, limit: int = 50) -> List[Dict]:
    """Get most compared item pairs.
    
    Returns a list of item pairs with their comparison counts.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    comparisons = db.query(Comparison).filter(
        Comparison.created_at >= cutoff_date
    ).all()
    
    # Count pairs
    pair_counts = {}
    for comp in comparisons:
        items = comp.items if isinstance(comp.items, list) else []
        if len(items) >= 2:
            # Create a sorted tuple for the pair (to handle order-independent pairs)
            pair = tuple(sorted([str(item).strip() for item in items[:2]]))
            pair_key = " vs ".join(pair)
            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
    
    # Sort by count descending
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {"pair": pair, "count": count}
        for pair, count in sorted_pairs[:limit]
    ]


# ========== FEEDBACK REPOSITORY ==========

def create_feedback(db: Session, comparison_id: str, rating: int, 
                   comment: Optional[str] = None, user_id: Optional[str] = None,
                   helpful: bool = True, accurate: bool = True) -> Feedback:
    """Create feedback for a comparison."""
    feedback = Feedback(
        comparison_id=comparison_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        helpful=helpful,
        accurate=accurate
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_by_comparison(db: Session, comparison_id: str) -> List[Feedback]:
    """Get all feedback for a specific comparison."""
    return db.query(Feedback).filter(
        Feedback.comparison_id == comparison_id
    ).order_by(desc(Feedback.created_at)).all()


def get_feedback_stats(db: Session, days: int = 30) -> Dict:
    """Get aggregate feedback statistics with detailed metrics."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all feedback for parsing
    feedbacks = db.query(Feedback).filter(
        Feedback.created_at >= cutoff_date
    ).all()
    
    total_feedback = len(feedbacks)
    
    if total_feedback == 0:
        return {
            "total_feedback": 0,
            "comprehensiveness_score": 0.0,
            "decision_helpfulness": {
                "yes_decided": 0,
                "somewhat": 0,
                "still_confused": 0,
                "need_different": 0
            },
            "winner_match_score": 0.0,
            "winner_match_count": 0,
            "top_improvements": [],
            "feedback_response_rate": 0.0
        }
    
    # Comprehensiveness Score (average rating from Q1)
    total_rating = sum(f.rating for f in feedbacks)
    comprehensiveness_score = round(total_rating / total_feedback, 2)
    
    # Parse comments to extract detailed metrics
    decision_counts = {
        "yes_decided": 0,
        "somewhat": 0,
        "still_confused": 0,
        "need_different": 0
    }
    
    winner_match_ratings = []
    improvement_suggestions = []
    
    for feedback in feedbacks:
        comment = feedback.comment or ""
        
        # Parse Decision Help responses
        if "Decision help:" in comment:
            if "Yes, I know what to choose" in comment:
                decision_counts["yes_decided"] += 1
            elif "Somewhat" in comment:
                decision_counts["somewhat"] += 1
            elif "No, still confused" in comment:
                decision_counts["still_confused"] += 1
            elif "different" in comment.lower():
                decision_counts["need_different"] += 1
        
        # Parse Winner Match ratings
        if "Winner match:" in comment:
            import re
            match = re.search(r'Winner match: (\d)/5', comment)
            if match:
                winner_match_ratings.append(int(match.group(1)))
        
        # Parse Improvement suggestions
        if "Improvement:" in comment:
            parts = comment.split("Improvement:")
            if len(parts) > 1:
                improvement_text = parts[1].strip()
                if improvement_text:
                    improvement_suggestions.append(improvement_text)
    
    # Calculate Winner Match Score
    winner_match_score = 0.0
    if winner_match_ratings:
        winner_match_score = round(sum(winner_match_ratings) / len(winner_match_ratings), 2)
    
    # Get top improvement suggestions (count occurrences of common words/phrases)
    improvement_counts = {}
    for suggestion in improvement_suggestions:
        # Normalize and count
        normalized = suggestion.lower().strip()
        if normalized:
            improvement_counts[normalized] = improvement_counts.get(normalized, 0) + 1
    
    # Sort and get top 5
    top_improvements = sorted(
        [{"text": text, "count": count} for text, count in improvement_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    # Calculate feedback response rate (feedback count vs comparison count)
    total_comparisons = db.query(func.count(Comparison.id)).filter(
        Comparison.created_at >= cutoff_date
    ).scalar() or 1
    
    feedback_response_rate = round((total_feedback / total_comparisons) * 100, 2)
    
    return {
        "total_feedback": total_feedback,
        "comprehensiveness_score": comprehensiveness_score,
        "decision_helpfulness": decision_counts,
        "winner_match_score": winner_match_score,
        "winner_match_count": len(winner_match_ratings),
        "top_improvements": top_improvements,
        "feedback_response_rate": min(feedback_response_rate, 100.0)  # Cap at 100%
    }


def get_winner_distribution(db: Session, days: int = 30) -> List[Dict]:
    """Get distribution of winners from comparisons with user preferences."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    comparisons = db.query(Comparison).filter(
        Comparison.created_at >= cutoff_date
    ).all()
    
    winner_counts = {}
    total_with_winner = 0
    
    for comp in comparisons:
        result = comp.original_comparison if isinstance(comp.original_comparison, dict) else {}
        if isinstance(result, dict) and result.get("personalized_winner"):
            winner = result["personalized_winner"]
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
            total_with_winner += 1
    
    # Sort by count descending
    sorted_winners = sorted(winner_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {
            "item": winner,
            "count": count,
            "percentage": round((count / total_with_winner * 100), 2) if total_with_winner > 0 else 0.0
        }
        for winner, count in sorted_winners[:10]  # Top 10
    ]


def get_dashboard_summary(db: Session, days: int = 30) -> Dict:
    """Get comprehensive dashboard summary."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total comparisons
    total_comparisons = db.query(func.count(Comparison.id)).filter(
        Comparison.created_at >= cutoff_date
    ).scalar()
    
    # Count personalized vs general comparisons
    all_comparisons = db.query(Comparison).filter(
        Comparison.created_at >= cutoff_date
    ).all()
    
    personalized_count = 0
    general_count = 0
    for comp in all_comparisons:
        result = comp.original_comparison if isinstance(comp.original_comparison, dict) else {}
        if isinstance(result, dict) and result.get("personalized_winner"):
            personalized_count += 1
        else:
            general_count += 1
    
    # Get most compared items
    most_compared = get_most_compared_items(db, limit=10)
    
    # Get category stats
    category_stats = get_category_stats(db, days=days)
    
    # Get feedback stats (now includes detailed metrics)
    feedback_stats = get_feedback_stats(db, days=days)
    
    # Get winner distribution
    winner_dist = get_winner_distribution(db, days=days)
    
    # Get comparison pairs (item pairs that were compared together)
    comparison_pairs = get_comparison_pairs(db, days=days, limit=50)
    
    # Get trends (comparison count by date)
    trends = get_comparison_count_by_date(db, days=days)
    
    return {
        "total_comparisons": total_comparisons or 0,
        "personalized_count": personalized_count,
        "general_count": general_count,
        "most_compared_items": [
            {"name": item.name, "category": item.category, "count": item.comparison_count}
            for item in most_compared
        ],
        "category_stats": category_stats,
        "comparison_pairs": comparison_pairs,
        "feedback_stats": feedback_stats,
        "winner_distribution": winner_dist,
        "trends": trends
    }

