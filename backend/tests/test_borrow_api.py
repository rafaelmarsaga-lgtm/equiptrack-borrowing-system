from datetime import date, timedelta

from app.models import BorrowRecord
from app.timeutil import today_ph


def add_equipment(client, name="Dell Latitude laptop", category="Laptop", total=5):
    return client.post(
        "/api/equipment", json={"name": name, "category": category, "total_quantity": total}
    ).json()


def borrow(client, equipment_id, quantity=1, **overrides):
    payload = {
        "borrower_name": "Maria Santos",
        "id_number": "2023-00123",
        "borrower_type": "Student",
        "equipment_id": equipment_id,
        "quantity": quantity,
        "due_date": (today_ph() + timedelta(days=7)).isoformat(),
    }
    payload.update(overrides)
    return client.post("/api/borrows", json=payload)


def available_of(client, equipment_id):
    items = client.get("/api/equipment").json()
    return next(item["available"] for item in items if item["id"] == equipment_id)


def test_successful_borrow_returns_201_and_reduces_available(client):
    item = add_equipment(client, total=5)
    due = (today_ph() + timedelta(days=7)).isoformat()

    response = borrow(client, item["id"], quantity=2, due_date=due)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["due_date"] == due
    assert body["quantity"] == 2
    assert body["equipment_name"] == "Dell Latitude laptop"
    assert body["return_date"] is None
    assert available_of(client, item["id"]) == 3


def test_borrow_date_is_today_in_philippine_time(client, monkeypatch):
    # 2026-10-02 stands in for "today in the Philippines"
    monkeypatch.setattr("app.services.borrow_service.today_ph", lambda: date(2026, 10, 2))
    item = add_equipment(client)
    response = borrow(client, item["id"], due_date="2026-10-05")
    assert response.json()["borrow_date"] == "2026-10-02"


def test_borrowing_more_than_available_is_rejected_with_400(client):
    item = add_equipment(client, total=5)
    borrow(client, item["id"], quantity=3)

    response = borrow(client, item["id"], quantity=3)  # only 2 left

    assert response.status_code == 400
    assert response.json() == {"detail": "Only 2 available; you asked for 3."}
    assert available_of(client, item["id"]) == 2  # nothing was saved


def test_borrowing_unknown_equipment_is_rejected_with_404(client):
    response = borrow(client, equipment_id=999)
    assert response.status_code == 404
    assert response.json() == {"detail": "Equipment not found."}


def test_borrowing_exactly_the_available_amount_is_allowed_and_leaves_zero(client):
    item = add_equipment(client, total=4)

    first = borrow(client, item["id"], quantity=4)
    assert first.status_code == 201
    assert available_of(client, item["id"]) == 0

    second = borrow(client, item["id"], quantity=1)
    assert second.status_code == 400
    assert second.json() == {"detail": "Only 0 available; you asked for 1."}


def test_returned_records_do_not_count_against_availability(client, db):
    item = add_equipment(client, total=5)
    db.add(BorrowRecord(
        equipment_id=item["id"], borrower_name="Ana Cruz", id_number="2024-00456",
        borrower_type="Student", quantity=4, borrow_date=date(2026, 9, 25),
        due_date=date(2026, 9, 30), return_date=date(2026, 9, 29),
    ))
    db.commit()
    assert available_of(client, item["id"]) == 5

    response = borrow(client, item["id"], quantity=5)  # all 5 are on the shelf

    assert response.status_code == 201
    assert available_of(client, item["id"]) == 0
