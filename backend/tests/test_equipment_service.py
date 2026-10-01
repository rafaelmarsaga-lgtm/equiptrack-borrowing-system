from datetime import date

from app.models import BorrowRecord, Equipment
from app.services.equipment_service import available_quantity, escape_like


def make_equipment(db, total=10):
    item = Equipment(name="Laptop", name_key="laptop", category="Laptop", total_quantity=total)
    db.add(item)
    db.commit()
    return item


def make_borrow(db, equipment_id, quantity, return_date=None):
    db.add(BorrowRecord(
        equipment_id=equipment_id, borrower_name="Maria Santos", id_number="2023-00123",
        borrower_type="Student", quantity=quantity, borrow_date=date(2026, 10, 1),
        due_date=date(2026, 10, 8), return_date=return_date,
    ))
    db.commit()


def test_escape_like_escapes_percent_underscore_and_backslash():
    assert escape_like("100%") == r"100\%"
    assert escape_like("a_b") == r"a\_b"
    # "a\\b" is the 3-character string a, backslash, b. Its backslash must be doubled.
    assert escape_like("a\\b") == "a\\\\b"


def test_escape_like_leaves_plain_text_alone():
    assert escape_like("laptop") == "laptop"


def test_available_is_total_when_nothing_borrowed(db):
    item = make_equipment(db, total=10)
    assert available_quantity(db, item.id) == 10


def test_available_subtracts_unreturned_borrows(db):
    item = make_equipment(db, total=10)
    make_borrow(db, item.id, 3)
    make_borrow(db, item.id, 2)
    assert available_quantity(db, item.id) == 5


def test_available_ignores_returned_borrows(db):
    item = make_equipment(db, total=10)
    make_borrow(db, item.id, 4, return_date=date(2026, 10, 2))
    assert available_quantity(db, item.id) == 10
