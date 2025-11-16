"""
Database connection and session management for the Compair API.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from utilities.constants import DATABASE_URL

logger = logging.getLogger(__name__)

# Create database engine
# Use StaticPool for SQLite, or optimized pool for PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    # Optimized connection pool for PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,              # Number of persistent connections
        max_overflow=10,           # Additional connections under load
        pool_timeout=30,           # Seconds to wait for connection
        pool_recycle=3600,         # Recycle connections after 1 hour
        pool_pre_ping=True,        # Verify connections before use
        connect_args={
            "options": "-c statement_timeout=30000"  # 30 second query timeout
        }
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function for FastAPI to get database session.
    Use this in route handlers: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Usage:
        with get_db_session() as db:
            # use db here
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables."""
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """Drop all database tables (use with caution!)."""
    from database.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")

