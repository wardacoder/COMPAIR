"""
Database package initialization.

This package contains all database-related modules including models,
connection management, and repository functions.
"""

from database.models import (
    Base,
    SharedComparison,
    Comparison,
    ComparisonCache,
    Item,
    Feedback
)

from database.connection import (
    get_db,
    get_db_session,
    init_db,
    drop_db,
    engine,
    SessionLocal
)

__all__ = [
    "Base",
    "SharedComparison",
    "Comparison",
    "ComparisonCache",
    "Item",
    "Feedback",
    "get_db",
    "get_db_session",
    "init_db",
    "drop_db",
    "engine",
    "SessionLocal",
]

