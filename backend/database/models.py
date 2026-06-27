"""
SQLAlchemy database models for the Compair API.

This module contains all database models (ORM) for the application.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import String as SQLString
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import os

Base = declarative_base()

# Use UUID for PostgreSQL, String for SQLite
def UUIDColumn():
    """Return appropriate UUID column type based on database."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./compair.db")
    if db_url.startswith("postgresql"):
        return Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


def UUIDForeignKey(table_name):
    """Return appropriate UUID foreign key column."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./compair.db")
    if db_url.startswith("postgresql"):
        return Column(PG_UUID(as_uuid=True), ForeignKey(table_name), nullable=False)
    else:
        return Column(String(36), ForeignKey(table_name), nullable=False)


class SharedComparison(Base):
    """Shared comparison model for public sharing."""
    __tablename__ = "shared_comparisons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    share_id = Column(String(8), unique=True, nullable=False, index=True)
    comparison_id = Column(String(36), nullable=True)  # Reference to comparison, not a foreign key
    category = Column(String(100), nullable=False)
    # Use JSONB for PostgreSQL (better performance), fallback to JSON for SQLite
    items = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    result = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    views = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Partial index for active shared comparisons (PostgreSQL-specific)
    __table_args__ = (
        Index('ix_shared_comparisons_active', 'created_at', postgresql_where=(expires_at.is_(None) | (expires_at > datetime.utcnow()))),
    )


class Comparison(Base):
    """Comparison model for storing comparison data and follow-up question history.
    
    This is the primary table for storing comparison data and analytics.
    Each comparison creates an entry immediately for follow-ups and dashboard analytics.
    """
    __tablename__ = "comparisons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comparison_id = Column(String(36), nullable=False, unique=True, index=True)  # Unique identifier for the comparison
    # Use JSONB for PostgreSQL (better performance), fallback to JSON for SQLite
    messages = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    original_comparison = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    items = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for common query patterns
    __table_args__ = (
        Index('ix_comparisons_category_created', 'category', 'created_at'),
    )


class ComparisonCache(Base):
    """Cache model for storing cached comparison results."""
    __tablename__ = "comparison_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(100), nullable=False, index=True)
    # Use JSONB for PostgreSQL (better performance), fallback to JSON for SQLite
    items = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    user_preferences = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=True)
    result = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True, index=True)

    # Partial index for cache cleanup (PostgreSQL-specific)
    __table_args__ = (
        Index('ix_comparison_cache_cleanup', 'expires_at', postgresql_where=expires_at.isnot(None)),
    )


class Item(Base):
    """Item model for tracking popular items."""
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    # Use JSONB for PostgreSQL (better performance), fallback to JSON for SQLite
    item_metadata = Column(JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON, nullable=True)
    comparison_count = Column(Integer, default=0)  # How many times this item was compared
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Feedback(Base):
    """Feedback model for user ratings and comments on comparisons.
    
    References comparisons table.
    """
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comparison_id = Column(String(36), nullable=False, index=True)  # Reference to comparison's comparison_id field
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    comment = Column(Text, nullable=True)  # Optional text comment
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for common queries
    __table_args__ = (
        Index('ix_feedback_comparison_created', 'comparison_id', 'created_at'),
    )

