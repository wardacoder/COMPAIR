"""
Data storage utilities for the Compair API.

This module handles database operations for comparison history, shared comparisons,
and conversation follow-ups. It replaces the previous JSON file-based storage.
"""

from database.connection import get_db_session
from database.repository import (
    create_comparison,
    get_user_comparisons,
    delete_comparison as db_delete_comparison,
    create_shared_comparison,
    get_shared_comparison as db_get_shared_comparison,
    increment_shared_views,
    create_conversation,
    get_conversation as db_get_conversation,
    add_message_to_conversation,
    get_cached_comparison,
    cache_comparison,
)
from datetime import datetime
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
import json

# In-memory storage for active conversation sessions (can be migrated to Redis later)
conversation_memory = {}


def load_history(user_id: str, limit: int = 100, offset: int = 0, category: str = None):
    """
    Load comparison history from database for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of results to return
        offset: Number of results to skip
        category: Optional category filter
    
    Returns:
        List of comparison dictionaries
    """
    with get_db_session() as db:
        comparisons = get_user_comparisons(db, user_id, limit, offset, category)
        return [
            {
                "timestamp": comp.created_at.isoformat(),
                "category": comp.category,
                "items": comp.items,
                "result": comp.result,
                "id": str(comp.id)
            }
            for comp in comparisons
        ]


def save_history(user_id: str, category: str, items: list, result: dict):
    """
    Save comparison to database.
    
    Args:
        user_id: User identifier
        category: Comparison category
        items: List of items compared
        result: Comparison result dictionary
    
    Returns:
        Created comparison entry
    """
    with get_db_session() as db:
        comparison = create_comparison(db, user_id, category, items, result)
        return {
            "timestamp": comparison.created_at.isoformat(),
            "category": comparison.category,
            "items": comparison.items,
            "result": comparison.result,
            "id": str(comparison.id)
        }


def load_shared(share_id: str):
    """
    Load shared comparison from database.
    
    Args:
        share_id: Share identifier
    
    Returns:
        Shared comparison dictionary or None
    """
    with get_db_session() as db:
        shared = db_get_shared_comparison(db, share_id)
        if shared:
            return {
                "share_id": shared.share_id,
                "category": shared.category,
                "items": shared.items,
                "result": shared.result,
                "created_at": shared.created_at.isoformat(),
                "user_id": str(shared.user_id) if shared.user_id else None,
                "views": shared.views
            }
        return None


def save_shared(share_id: str, comparison_id: str, category: str, items: list, 
               result: dict, user_id: str = None):
    """
    Save shared comparison to database.
    
    Args:
        share_id: Unique share identifier
        comparison_id: Original comparison ID
        category: Comparison category
        items: List of items compared
        result: Comparison result dictionary
        user_id: Optional user identifier
    
    Returns:
        Created shared comparison entry
    """
    with get_db_session() as db:
        shared = create_shared_comparison(
            db, comparison_id, share_id, category, items, result, user_id
        )
        return {
            "share_id": shared.share_id,
            "category": shared.category,
            "items": shared.items,
            "result": shared.result,
            "created_at": shared.created_at.isoformat(),
            "views": shared.views
        }


def increment_shared_view_count(share_id: str):
    """
    Increment view count for shared comparison.
    
    Args:
        share_id: Share identifier
    
    Returns:
        Updated view count
    """
    with get_db_session() as db:
        shared = increment_shared_views(db, share_id)
        return shared.views if shared else 0


def get_conversation_from_db(comparison_id: str):
    """
    Get conversation from database by comparison_id.
    
    Args:
        comparison_id: Comparison identifier
    
    Returns:
        Conversation data dictionary or None
    """
    with get_db_session() as db:
        conversation = db_get_conversation(db, comparison_id)
        if conversation:
            return {
                "comparison_id": str(conversation.comparison_id),
                "messages": conversation.messages,
                "original_comparison": conversation.original_comparison,
                "items": conversation.items,
                "category": conversation.category
            }
        return None


def save_conversation_to_db(comparison_id: str, original_comparison: dict,
                            items: list, category: str, user_id: str = None):
    """
    Save conversation to database.
    
    Args:
        comparison_id: Comparison identifier
        original_comparison: Original comparison result
        items: List of items compared
        category: Comparison category
        user_id: Optional user identifier
    
    Returns:
        Created conversation
    """
    with get_db_session() as db:
        conversation = create_conversation(
            db, comparison_id, user_id, original_comparison, items, category
        )
        return conversation


def add_conversation_message(comparison_id: str, role: str, content: str):
    """
    Add a message to conversation in database.
    
    Args:
        comparison_id: Comparison identifier
        role: Message role ('user' or 'assistant')
        content: Message content
    """
    with get_db_session() as db:
        add_message_to_conversation(db, comparison_id, role, content)


def get_cached_comparison_result(category: str, items: list, user_preferences: dict = None):
    """
    Get cached comparison if available.
    
    Args:
        category: Comparison category
        items: List of items
        user_preferences: Optional user preferences
    
    Returns:
        Cached result or None
    """
    with get_db_session() as db:
        cache = get_cached_comparison(db, category, items, user_preferences)
        return cache.result if cache else None


def save_cached_comparison(category: str, items: list, result: dict, user_preferences: dict = None):
    """
    Cache a comparison result.
    
    Args:
        category: Comparison category
        items: List of items
        result: Comparison result
        user_preferences: Optional user preferences
    """
    with get_db_session() as db:
        cache_comparison(db, category, items, result, user_preferences)


def delete_history_item(user_id: str, comparison_id: str):
    """
    Delete a comparison from history.
    
    Args:
        user_id: User identifier
        comparison_id: Comparison identifier
    
    Returns:
        True if deleted, False otherwise
    """
    with get_db_session() as db:
        return db_delete_comparison(db, user_id, comparison_id)
