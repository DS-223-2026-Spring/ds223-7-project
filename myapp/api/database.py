"""
Database session factory.

Uses the internal Docker hostname `db` — never `localhost`.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@db:5432/pulse",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """FastAPI dependency — yields a DB session, closes it after the
    request finishes."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
