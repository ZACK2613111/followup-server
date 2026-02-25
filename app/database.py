"""
Database configuration for FollowUp API.
Manages SQLAlchemy engine, session, and base model.
"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create engine with connection pool settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Verify connections before use
    pool_recycle=3600,        # Recycle connections every hour
    pool_size=10,             # Max connections in pool
    max_overflow=20,          # Extra connections allowed beyond pool_size
    echo=settings.DEBUG,      # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """
    Dependency injection for database sessions.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()