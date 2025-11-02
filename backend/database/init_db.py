"""
Database initialization script for the Compair API.

Run this script to initialize the database and create all tables.
"""

from database.connection import init_db, drop_db
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready."""
    from utilities.constants import DATABASE_URL
    from sqlalchemy import create_engine, text
    
    logger.info(f"Waiting for database at {DATABASE_URL}...")
    
    for i in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database is ready!")
            return True
        except Exception as e:
            if i < max_retries - 1:
                logger.info(f"Database not ready yet, retrying in {delay} seconds... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                return False
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        if wait_for_db():
            confirm = input("Are you sure you want to drop all tables? (yes/no): ")
            if confirm.lower() == "yes":
                drop_db()
                print("All tables dropped.")
            else:
                print("Cancelled.")
    else:
        if wait_for_db():
            init_db()
            print("Database initialized successfully!")
        else:
            print("Failed to connect to database. Exiting.")
            sys.exit(1)

