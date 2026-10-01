from datetime import date, timedelta

from app.models import BorrowRecord
from app.timeutil import today_ph


def add_equipment(client, name="Dell Latitude laptop", category="Laptop", total=5):
    return client.post(
        "/api/equipment", json={"name": name, "category": category, "total_quantity": total}
    ).json()


def borrow(client, equipment_id, quantity=1, due_date=None):
    return client.post("/api/borrows", json={
        "borrower_name": "Maria Santos", "id_number": "2023-00123", "borrower_type": "Student",
        "equipment_id": equipment_id, "quantity": quantity,
        "due_date": due_date or (today_ph() + timedelta(days=7)).isoformat(),
    })


def insert_record(db, equipment_id, due_date, return_date=None, quantity=1, name="Historic Borrower"):
    """Historical data the API would refuse to create (past due dates)."""
    record = BorrowRecord(
        equipment_id=equipment_id, borrower_name=name, id_number="2023-99999",
        borrower_type="Student", quantity=quantity, borrow_date=due_date - timedelta(days=7),
        due_date=due_date, return_date=return_date,
    )
    db.add(record)
    db.commit()
    return record


def available_of(client, equipment_id):
    items = client.get("/api/equipment").json()
    return next(item["available"] for item in items if item["id"] == equipment_id)


def test_return_sets_today_marks_returned_and_restores_availability(client, monkeypatch):
    monkeypatch.setattr("app.services.borrow_service.today_ph", lambda: date(2026, 10, 2))
    item = add_equipment(client, total=5)
    # The test's "today" is faked as Oct 2, so the due date must fall inside Oct 2..Oct 16.
    record = borrow(client, item["id"], quantity=2, due_date="2026-10-05").json()
    assert available_of(client, item["id"]) == 3

    response = client.post(f"/api/borrows/{record['id']}/return")

    assert response.status_code == 200
    body = response.json()
    assert body["return_date"] == "2026-10-02"
    assert body["status"] == "Returned"
    assert available_of(client, item["id"]) == 5


def test_returning_twice_is_rejected_with_400(client):
    item = add_equipment(client)
    record = borrow(client, item["id"]).json()
    client.post(f"/api/borrows/{record['id']}/return")

    response = client.post(f"/api/borrows/{record['id']}/return")

    assert response.status_code == 400
    assert response.json() == {"detail": "This item was already returned."}


def test_returning_unknown_record_is_rejected_with_404(client):
    response = client.post("/api/borrows/999/return")
    assert response.status_code == 404
    assert response.json() == {"detail": "Borrow record not found."}


def test_new_borrow_reports_status_borrowed(client):
    item = add_equipment(client)
    assert borrow(client, item["id"]).json()["status"] == "Borrowed"


def test_list_shows_computed_status_and_equipment_name(client, db):
    item = add_equipment(client, total=10)
    today = today_ph()
    borrow(client, item["id"])  # due in 7 days -> Borrowed
    insert_record(db, item["id"], due_date=today - timedelta(days=1), name="Late Person")  # Overdue
    insert_record(db, item["id"], due_date=today - timedelta(days=5), return_date=today - timedelta(days=3), name="Done Person")  # Returned

    rows = {row["borrower_name"]: row for row in client.get("/api/borrows").json()}

    assert rows["Maria Santos"]["status"] == "Borrowed"
    assert rows["Late Person"]["status"] == "Overdue"
    assert rows["Done Person"]["status"] == "Returned"
    assert rows["Late Person"]["equipment_name"] == "Dell Latitude laptop"


def test_list_is_newest_first(client):
    item = add_equipment(client, total=10)
    first = borrow(client, item["id"]).json()
    second = borrow(client, item["id"]).json()
    ids = [row["id"] for row in client.get("/api/borrows").json()]
    assert ids == [second["id"], first["id"]]


def test_status_filter_uses_the_computed_status(client, db):
    item = add_equipment(client, total=10)
    today = today_ph()
    borrow(client, item["id"])
    insert_record(db, item["id"], due_date=today - timedelta(days=1), name="Late Person")
    insert_record(db, item["id"], due_date=today - timedelta(days=5), return_date=today - timedelta(days=3), name="Done Person")

    def names_for(status):
        rows = client.get("/api/borrows", params={"status": status}).json()
        return [row["borrower_name"] for row in rows]

    assert names_for("Borrowed") == ["Maria Santos"]
    assert names_for("Overdue") == ["Late Person"]
    assert names_for("Returned") == ["Done Person"]


def test_overdue_items_still_count_as_borrowed_out(client, db):
    item = add_equipment(client, total=5)
    insert_record(db, item["id"], due_date=today_ph() - timedelta(days=2), quantity=2)
    assert available_of(client, item["id"]) == 3
