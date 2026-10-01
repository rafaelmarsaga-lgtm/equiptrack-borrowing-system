"""One test (or a small group) per row of the validation table in docs/PLAN.md section 9.
Every check asserts the status code AND the exact friendly message, and that
no raw Pydantic wording ("Input should ...") ever reaches the user."""
from datetime import timedelta

import pytest

from app.errors import friendly_message
from app.timeutil import today_ph

EQUIPMENT_OK = {"name": "Dell Latitude laptop", "category": "Laptop", "total_quantity": 5}

NAME_MSG = "Equipment name must be 2 to 60 characters."
CATEGORY_MSG = "Choose a valid category."
TOTAL_MSG = "Total quantity must be a whole number from 1 to 100."
FULL_NAME_MSG = "Full name must be 2 to 100 characters."
ID_MSG = "ID number must be 4 to 20 letters, digits or dashes."
TYPE_MSG = "Select Student or Faculty."
QUANTITY_MSG = "Quantity must be at least 1."
QUANTITY_WHOLE_MSG = "Quantity must be a whole number of at least 1."
DUE_INVALID_MSG = "Enter a valid due date."
DUE_WINDOW_MSG = "Due date must be between today and 14 days from today."
GENERIC_MSG = "Please check your entries and try again."


def post_equipment(client, **overrides):
    return client.post("/api/equipment", json={**EQUIPMENT_OK, **overrides})


def borrow_payload(equipment_id, **overrides):
    payload = {
        "borrower_name": "Maria Santos",
        "id_number": "2023-00123",
        "borrower_type": "Student",
        "equipment_id": equipment_id,
        "quantity": 1,
        "due_date": (today_ph() + timedelta(days=7)).isoformat(),
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def item(client):
    return post_equipment(client, total_quantity=10).json()


def assert_rejected(response, status, message):
    assert response.status_code == status
    assert response.json() == {"detail": message}
    assert "Input should" not in response.text


# ---- Equipment name: 2-60 chars after trim ---------------------------------

@pytest.mark.parametrize("name", ["a", "   ", " a ", "x" * 61])
def test_equipment_name_length_is_422(client, name):
    assert_rejected(post_equipment(client, name=name), 422, NAME_MSG)


@pytest.mark.parametrize("name", ["ab", "x" * 60, "  padded name  "])
def test_equipment_name_boundaries_are_accepted(client, name):
    assert post_equipment(client, name=name).status_code == 201


def test_equipment_name_is_stored_trimmed(client):
    assert post_equipment(client, name="  Spaced  ").json()["name"] == "Spaced"


# ---- Equipment name: unique, case-insensitive (409) -------------------------

def test_duplicate_equipment_name_is_409(client):
    post_equipment(client, name="Dell Latitude laptop")
    response = post_equipment(client, name="  DELL latitude LAPTOP ")
    assert_rejected(response, 409, "That equipment already exists.")


# ---- Category: one of the six ----------------------------------------------

@pytest.mark.parametrize("category", ["", "Nonsense", "laptop", None])
def test_category_must_be_one_of_the_six_422(client, category):
    assert_rejected(post_equipment(client, category=category), 422, CATEGORY_MSG)


@pytest.mark.parametrize("category", ["Laptop", "Projector", "Camera", "Audio", "Networking", "Others"])
def test_all_six_categories_are_accepted(client, category):
    assert post_equipment(client, name=f"Item {category}", category=category).status_code == 201


# ---- Total quantity: whole number 1-100 --------------------------------------

@pytest.mark.parametrize("total", [0, -5, 101, 100000, 1.5, "abc", None])
def test_total_quantity_range_and_type_is_422(client, total):
    assert_rejected(post_equipment(client, total_quantity=total), 422, TOTAL_MSG)


@pytest.mark.parametrize("total", [1, 100])
def test_total_quantity_boundaries_are_accepted(client, total):
    assert post_equipment(client, total_quantity=total).status_code == 201


# ---- Borrower full name: 2-100 chars after trim -----------------------------

@pytest.mark.parametrize("name", ["M", "   ", "x" * 101])
def test_borrower_name_length_is_422(client, item, name):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], borrower_name=name))
    assert_rejected(response, 422, FULL_NAME_MSG)


@pytest.mark.parametrize("name", ["Mo", "x" * 100])
def test_borrower_name_boundaries_are_accepted(client, item, name):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], borrower_name=name))
    assert response.status_code == 201


# ---- ID number: 4-20 chars, letters / digits / dashes only ------------------

@pytest.mark.parametrize("id_number", ["abc", "x" * 21, "ab!!", "ab!", "ab cd", "ab_cd", "    ", "2023/001"])
def test_id_number_pattern_is_422(client, item, id_number):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], id_number=id_number))
    assert_rejected(response, 422, ID_MSG)


@pytest.mark.parametrize("id_number", ["ABCD", "x" * 20, "2023-00123", "a-1-"])
def test_id_number_valid_forms_are_accepted(client, item, id_number):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], id_number=id_number))
    assert response.status_code == 201


# ---- Borrower type: Student / Faculty ---------------------------------------

@pytest.mark.parametrize("borrower_type", ["", "Alien", "student", None])
def test_borrower_type_must_be_student_or_faculty_422(client, item, borrower_type):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], borrower_type=borrower_type))
    assert_rejected(response, 422, TYPE_MSG)


@pytest.mark.parametrize("borrower_type", ["Student", "Faculty"])
def test_both_borrower_types_are_accepted(client, item, borrower_type):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], borrower_type=borrower_type))
    assert response.status_code == 201


# ---- Equipment id must exist (404) ------------------------------------------

def test_unknown_equipment_is_404(client):
    response = client.post("/api/borrows", json=borrow_payload(999))
    assert_rejected(response, 404, "Equipment not found.")


# ---- Quantity: integer >= 1, and <= available --------------------------------

@pytest.mark.parametrize("quantity", [0, -1, -3])
def test_quantity_below_one_is_422(client, item, quantity):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], quantity=quantity))
    assert_rejected(response, 422, QUANTITY_MSG)


@pytest.mark.parametrize("quantity", [1.5, "abc", None])
def test_quantity_that_is_not_a_whole_number_is_422(client, item, quantity):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], quantity=quantity))
    assert_rejected(response, 422, QUANTITY_WHOLE_MSG)


def test_quantity_above_available_is_400(client, item):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], quantity=11))
    assert_rejected(response, 400, "Only 10 available; you asked for 11.")


# ---- Due date: valid date, then today <= date <= today + 14 -----------------

@pytest.mark.parametrize("due", ["tomorrow", "2026-13-45", "2026-02-30", "", "10/08/2026", None])
def test_malformed_due_date_is_422(client, item, due):
    response = client.post("/api/borrows", json=borrow_payload(item["id"], due_date=due))
    assert_rejected(response, 422, DUE_INVALID_MSG)


def test_missing_due_date_is_422(client, item):
    payload = borrow_payload(item["id"])
    del payload["due_date"]
    assert_rejected(client.post("/api/borrows", json=payload), 422, DUE_INVALID_MSG)


@pytest.mark.parametrize("days", [-1, -30, 15, 400])
def test_due_date_outside_the_window_is_400(client, item, days):
    due = (today_ph() + timedelta(days=days)).isoformat()
    response = client.post("/api/borrows", json=borrow_payload(item["id"], due_date=due))
    assert_rejected(response, 400, DUE_WINDOW_MSG)


@pytest.mark.parametrize("days", [0, 14])
def test_due_date_window_boundaries_are_accepted(client, item, days):
    due = (today_ph() + timedelta(days=days)).isoformat()
    response = client.post("/api/borrows", json=borrow_payload(item["id"], due_date=due))
    assert response.status_code == 201


# ---- Return: record exists (404), not already returned (400) ----------------

def test_return_unknown_record_is_404(client):
    assert_rejected(client.post("/api/borrows/999/return"), 404, "Borrow record not found.")


def test_return_twice_is_400(client, item):
    record = client.post("/api/borrows", json=borrow_payload(item["id"])).json()
    client.post(f"/api/borrows/{record['id']}/return")
    response = client.post(f"/api/borrows/{record['id']}/return")
    assert_rejected(response, 400, "This item was already returned.")


# ---- Every 422 is friendly, including empty, broken and nested bodies --------

def test_empty_equipment_form_names_the_first_problem(client):
    assert_rejected(client.post("/api/equipment", json={}), 422, NAME_MSG)


def test_empty_borrow_form_names_the_first_problem(client):
    assert_rejected(client.post("/api/borrows", json={}), 422, FULL_NAME_MSG)


def test_body_that_is_not_json_is_422_with_friendly_text(client):
    response = client.post("/api/equipment", content="{broken", headers={"Content-Type": "application/json"})
    assert_rejected(response, 422, "The request could not be read. Please check your entries and try again.")


def test_body_that_is_not_an_object_is_422_with_friendly_text(client):
    assert_rejected(client.post("/api/borrows", json=[1, 2, 3]), 422, GENERIC_MSG)


def test_non_numeric_record_id_in_the_path_is_422_with_friendly_text(client):
    assert_rejected(client.post("/api/borrows/abc/return"), 422, GENERIC_MSG)


def test_nested_field_errors_use_the_last_field_name():
    errors = [{"type": "greater_than_equal", "loc": ("body", "items", 0, "quantity"), "msg": "Input should be greater than or equal to 1"}]
    assert friendly_message(errors) == QUANTITY_MSG


def test_nested_whole_number_error_uses_the_whole_number_message():
    errors = [{"type": "int_from_float", "loc": ("body", "items", 3, "quantity"), "msg": "Input should be a valid integer"}]
    assert friendly_message(errors) == QUANTITY_WHOLE_MSG


def test_unknown_field_gets_the_generic_message():
    errors = [{"type": "missing", "loc": ("body", "mystery"), "msg": "Field required"}]
    assert friendly_message(errors) == GENERIC_MSG
