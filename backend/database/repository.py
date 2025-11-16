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
    User, Comparison, SharedComparison, Conversation, ComparisonCache, Item
)
from utilities.constants import DATABASE_URL

logger = logging.getLogger(__name__)


# ========== USER REPOSITORY ==========

def create_user(db: Session, email: Optional[str] = None, username: Optional[str] = None, 
                preferences: Optional[Dict] = None) -> User:
    """Create a new user."""
    user = User(email=email, username=username, preferences=preferences)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def update_user_preferences(db: Session, user_id: str, preferences: Dict) -> Optional[User]:
    """Update user preferences."""
    user = get_user(db, user_id)
    if user:
        user.preferences = preferences
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user


# ========== COMPARISON REPOSITORY ==========

def create_comparison(db: Session, user_id: str, category: str, items: List[str], 
                     result: Dict) -> Comparison:
    """Create a new comparison."""
    # Get or create user
    user = get_user(db, user_id)
    if not user:
        user = create_user(db)
        user_id = str(user.id)
    
    comparison = Comparison(
        user_id=user_id,
        category=category,
        items=items,
        result=result
    )
    db.add(comparison)
    
    # Update item comparison counts
    for item_name in items:
        item = db.query(Item).filter(Item.name == item_name).first()
        if item:
            item.comparison_count += 1
            item.updated_at = datetime.utcnow()
        else:
            item = Item(name=item_name, category=category, comparison_count=1)
            db.add(item)
    
    db.commit()
    db.refresh(comparison)
    return comparison


def get_comparison(db: Session, comparison_id: str) -> Optional[Comparison]:
    """Get comparison by ID."""
    return db.query(Comparison).filter(Comparison.id == comparison_id).first()


def get_user_comparisons(db: Session, user_id: str, limit: int = 20, 
                         offset: int = 0, category: Optional[str] = None) -> List[Comparison]:
    """Get comparisons for a user with pagination and optional category filter.
    
    Uses eager loading to prevent N+1 query problems.
    """
    query = db.query(Comparison)\
        .options(joinedload(Comparison.user))\
        .options(joinedload(Comparison.shared_comparison))\
        .filter(Comparison.user_id == user_id)
    
    if category:
        query = query.filter(Comparison.category == category)
    
    return query.order_by(desc(Comparison.created_at)).limit(limit).offset(offset).all()


def delete_comparison(db: Session, user_id: str, comparison_id: str) -> bool:
    """Delete a comparison."""
    comparison = db.query(Comparison).filter(
        and_(
            Comparison.id == comparison_id,
            Comparison.user_id == user_id
        )
    ).first()
    
    if comparison:
        db.delete(comparison)
        db.commit()
        return True
    return False


def search_comparisons(db: Session, user_id: str, search_term: str) -> List[Comparison]:
    """Search comparisons by items."""
    # PostgreSQL/JSON search
    query = db.query(Comparison).filter(Comparison.user_id == user_id)
    # Simple search - can be improved with full-text search
    results = []
    for comp in query.all():
        if any(search_term.lower() in str(item).lower() for item in comp.items):
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
        user_id=user_id if user_id else None,
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
        .options(joinedload(SharedComparison.comparison))\
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
                       original_comparison: Dict, items: List[str], category: str) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        comparison_id=comparison_id,
        user_id=user_id if user_id else None,
        messages=[],
        original_comparison=original_comparison,
        items=items,
        category=category
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, comparison_id: str) -> Optional[Conversation]:
    """Get conversation by comparison_id."""
    return db.query(Conversation).filter(
        Conversation.comparison_id == comparison_id
    ).first()


def add_message_to_conversation(db: Session, comparison_id: str, role: str, content: str) -> Optional[Conversation]:
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


def get_user_conversations(db: Session, user_id: str) -> List[Conversation]:
    """Get all conversations for a user."""
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(desc(Conversation.updated_at)).all()


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

