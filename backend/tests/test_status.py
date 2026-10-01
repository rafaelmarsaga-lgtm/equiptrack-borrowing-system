from datetime import date

from app.services.borrow_service import compute_status

TODAY = date(2026, 10, 10)


def test_unreturned_with_future_due_date_is_borrowed():
    assert compute_status(due_date=date(2026, 10, 15), return_date=None, today=TODAY) == "Borrowed"


def test_due_today_is_not_overdue():
    assert compute_status(due_date=TODAY, return_date=None, today=TODAY) == "Borrowed"


def test_due_yesterday_is_overdue():
    assert compute_status(due_date=date(2026, 10, 9), return_date=None, today=TODAY) == "Overdue"


def test_returned_is_returned_even_if_it_was_late():
    assert compute_status(due_date=date(2026, 9, 1), return_date=date(2026, 10, 5), today=TODAY) == "Returned"


def test_returned_on_time_is_returned():
    assert compute_status(due_date=date(2026, 10, 15), return_date=date(2026, 10, 9), today=TODAY) == "Returned"
