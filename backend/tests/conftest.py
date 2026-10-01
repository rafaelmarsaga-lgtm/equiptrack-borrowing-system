import os

# Must run BEFORE the app is imported, so tests use in-memory SQLite
# and never create the real equiptrack.db file.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app


@pytest.fixture
def client():
    # "with" runs the lifespan, which creates the tables.
    with TestClient(app) as test_client:
        yield test_client
    # The in-memory DB is shared, so wipe it to keep every test independent.
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """A direct DB session, for setting up data the API can't create yet
    (for example unreturned borrow records)."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
