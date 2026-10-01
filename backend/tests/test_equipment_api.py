from datetime import date

from app.models import BorrowRecord


def add(client, name, category="Laptop", total=5):
    return client.post("/api/equipment", json={"name": name, "category": category, "total_quantity": total})


def names(response):
    return [item["name"] for item in response.json()]


def test_list_is_empty_when_no_equipment(client):
    response = client.get("/api/equipment")
    assert response.status_code == 200
    assert response.json() == []


def test_add_equipment_returns_201_with_available_equal_to_total(client):
    response = add(client, "Dell Latitude laptop", "Laptop", 10)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Dell Latitude laptop"
    assert body["category"] == "Laptop"
    assert body["total_quantity"] == 10
    assert body["available"] == 10
    assert "id" in body


def test_duplicate_name_is_rejected_case_insensitively_with_409(client):
    add(client, "Dell Latitude laptop")
    response = add(client, "DELL LATITUDE LAPTOP")
    assert response.status_code == 409
    assert response.json() == {"detail": "That equipment already exists."}


def test_list_shows_live_available_count(client, db):
    created = add(client, "Dell Latitude laptop", total=10).json()
    db.add(BorrowRecord(
        equipment_id=created["id"], borrower_name="Maria Santos", id_number="2023-00123",
        borrower_type="Student", quantity=3, borrow_date=date(2026, 10, 1),
        due_date=date(2026, 10, 8), return_date=None,
    ))
    db.commit()
    item = client.get("/api/equipment").json()[0]
    assert item["total_quantity"] == 10
    assert item["available"] == 7


def test_search_is_case_insensitive_and_partial(client):
    add(client, "Dell Latitude laptop")
    add(client, "Epson projector", "Projector")
    assert names(client.get("/api/equipment", params={"search": "LAP"})) == ["Dell Latitude laptop"]


def test_search_percent_matches_only_names_containing_a_percent(client):
    add(client, "Dell Latitude laptop")
    add(client, "100% cotton cable", "Others")
    assert names(client.get("/api/equipment", params={"search": "%"})) == ["100% cotton cable"]


def test_search_underscore_matches_only_names_containing_an_underscore(client):
    add(client, "Dell Latitude laptop")
    add(client, "cam_01", "Camera")
    assert names(client.get("/api/equipment", params={"search": "_"})) == ["cam_01"]


def test_filter_by_category(client):
    add(client, "Dell Latitude laptop", "Laptop")
    add(client, "Canon DSLR camera", "Camera")
    assert names(client.get("/api/equipment", params={"category": "Camera"})) == ["Canon DSLR camera"]


def test_search_and_category_filter_work_together(client):
    add(client, "Dell Latitude laptop", "Laptop")
    add(client, "Lapel microphone", "Audio")
    response = client.get("/api/equipment", params={"search": "lap", "category": "Audio"})
    assert names(response) == ["Lapel microphone"]
