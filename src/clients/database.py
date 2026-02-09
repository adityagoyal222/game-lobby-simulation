"""
Simple Database Connection using Peewee ORM
Easy to use, no complex setup required
"""
import os
import logging
from peewee import PostgresqlDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database instance
db = PostgresqlDatabase(
    os.getenv("DB_NAME", "matchmaking_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432"))
)


def connect_db():
    """Connect to database"""
    try:
        # Only connect if not already connected
        if db.is_closed():
            db.connect()
            logger.info(f"Connected to database: {db.database}")
        else:
            logger.info(f"Already connected to database: {db.database}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False


def close_db():
    """Close database connection"""
    if not db.is_closed():
        db.close()
        logger.info("Database connection closed")


def init_db():
    """Initialize database (create tables)"""
    from src.models.user_model import UserModel

    try:
        db.create_tables([UserModel])
        logger.info("Database tables created")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False
