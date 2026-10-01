import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./equiptrack.db")

if DATABASE_URL == "sqlite://":
    # In-memory DB (tests): one shared connection, otherwise each new
    # connection would see its own empty database.
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SQLite stores integers as signed 64-bit. A bigger or smaller id cannot be
# stored, so no record can have it, and the driver raises OverflowError (HTTP
# 500) if we try to query with it.
SQLITE_MIN_INTEGER = -(2**63)
SQLITE_MAX_INTEGER = 2**63 - 1


def get_by_id(db, model, record_id: int):
    """Like db.get(), but an id outside SQLite's range simply returns None
    ("not found") without touching the database."""
    if not SQLITE_MIN_INTEGER <= record_id <= SQLITE_MAX_INTEGER:
        return None
    return db.get(model, record_id)
