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
    from sqlalchemy.exc import OperationalError
    
    try:
        # Test connection first
        with engine.connect() as conn:
            pass
        Base.metadata.create_all(bind=engine)
        db_display = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL
        logger.info(f"Database initialized successfully: {db_display}")
    except OperationalError as e:
        error_msg = str(e)
        logger.error("=" * 60)
        logger.error("DATABASE CONNECTION FAILED")
        logger.error("=" * 60)
        
        if "postgres" in DATABASE_URL.lower() and ("could not translate host name" in error_msg.lower() or "postgres" in error_msg.lower()):
            logger.error(f"Current DATABASE_URL: {DATABASE_URL}")
            logger.error("")
            logger.error("The hostname 'postgres' is typically used in Docker Compose.")
            logger.error("Since you're running locally, you have two options:")
            logger.error("")
            logger.error("OPTION 1 (Recommended for local dev): Use SQLite")
            logger.error("  Set environment variable: DATABASE_URL=sqlite:///./compair.db")
            logger.error("  Or create a .env file in the backend/ directory with:")
            logger.error("  DATABASE_URL=sqlite:///./compair.db")
            logger.error("")
            logger.error("OPTION 2: Use local PostgreSQL")
            logger.error("  Change DATABASE_URL to: postgresql://user:password@localhost:5432/compair")
            logger.error("  Make sure PostgreSQL is running locally")
        else:
            logger.error(f"Database connection error: {e}")
            logger.error(f"Current DATABASE_URL: {DATABASE_URL}")
        
        logger.error("=" * 60)
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.error(f"Current DATABASE_URL: {DATABASE_URL}")
        raise


def drop_db():
    """Drop all database tables (use with caution!)."""
    from database.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")

