"""Regression tests for a real error found while probing Step 6:
an id larger than SQLite's biggest integer crashed the server with HTTP 500
(OverflowError: Python int too large to convert to SQLite INTEGER).
A record with such an id can never exist, so the right answer is the normal 404."""
import json
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.timeutil import today_ph

SQLITE_MAX_INTEGER = 2**63 - 1
SQLITE_MIN_INTEGER = -(2**63)


@pytest.fixture
def server_like_client():
    # Behaves like the real server: an unhandled error becomes a 500 response
    # instead of being re-raised into the test.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def borrow_with_equipment_id(client, equipment_id):
    body = {
        "borrower_name": "Maria Santos",
        "id_number": "2023-00123",
        "borrower_type": "Student",
        "equipment_id": equipment_id,
        "quantity": 1,
        "due_date": (today_ph() + timedelta(days=3)).isoformat(),
    }
    # json.dumps keeps huge integers exact (they must not become floats)
    return client.post("/api/borrows", content=json.dumps(body), headers={"Content-Type": "application/json"})


@pytest.mark.parametrize(
    "record_id",
    [SQLITE_MAX_INTEGER, SQLITE_MAX_INTEGER + 1, 10**20, SQLITE_MIN_INTEGER, SQLITE_MIN_INTEGER - 1, -(10**20)],
)
def test_return_with_an_id_beyond_sqlite_range_is_404_not_500(server_like_client, record_id):
    response = server_like_client.post(f"/api/borrows/{record_id}/return")
    assert response.status_code == 404
    assert response.json() == {"detail": "Borrow record not found."}


@pytest.mark.parametrize(
    "equipment_id",
    [SQLITE_MAX_INTEGER, SQLITE_MAX_INTEGER + 1, 10**20, SQLITE_MIN_INTEGER, SQLITE_MIN_INTEGER - 1, -(10**20)],
)
def test_borrow_with_an_equipment_id_beyond_sqlite_range_is_404_not_500(server_like_client, equipment_id):
    response = borrow_with_equipment_id(server_like_client, equipment_id)
    assert response.status_code == 404
    assert response.json() == {"detail": "Equipment not found."}
