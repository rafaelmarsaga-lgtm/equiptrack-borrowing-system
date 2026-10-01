from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_by_id
from ..models import BorrowRecord, Equipment
from ..schemas import BorrowCreate, BorrowOut
from ..timeutil import today_ph
from .equipment_service import available_quantity


class EquipmentNotFoundError(Exception):
    """The requested equipment id does not exist."""


MAX_BORROW_DAYS = 14


class DueDateOutOfRangeError(Exception):
    """Due date is before today or more than 14 days ahead."""


class BorrowNotFoundError(Exception):
    """The requested borrow record does not exist."""


class AlreadyReturnedError(Exception):
    """The record was already marked returned."""


class NotEnoughStockError(Exception):
    def __init__(self, available: int, requested: int):
        self.available = available
        self.requested = requested
        super().__init__(f"Only {available} available; you asked for {requested}.")


def create_borrow(db: Session, data: BorrowCreate) -> BorrowOut:
    equipment = get_by_id(db, Equipment, data.equipment_id)
    if equipment is None:
        raise EquipmentNotFoundError(data.equipment_id)

    # "Today" is Philippine time, so the window is the same for everyone.
    today = today_ph()
    if not today <= data.due_date <= today + timedelta(days=MAX_BORROW_DAYS):
        raise DueDateOutOfRangeError(data.due_date)

    # Always re-checked on the server: the page's availability may be stale
    # if someone else borrowed in the meantime.
    available = available_quantity(db, equipment.id)
    if data.quantity > available:
        raise NotEnoughStockError(available, data.quantity)

    record = BorrowRecord(
        equipment_id=equipment.id,
        borrower_name=data.borrower_name.strip(),
        id_number=data.id_number.strip(),
        borrower_type=data.borrower_type,
        quantity=data.quantity,
        borrow_date=today_ph(),
        due_date=data.due_date,
    )
    db.add(record)
    db.commit()
    return to_out(record, equipment.name)


def compute_status(due_date: date, return_date: date | None, today: date) -> str:
    """Status is derived, never stored, so it can't disagree with the dates.
    Due today is still Borrowed: it only becomes Overdue the day after."""
    if return_date is not None:
        return "Returned"
    if due_date < today:
        return "Overdue"
    return "Borrowed"


def list_borrows(db: Session, status: str | None = None) -> list[BorrowOut]:
    rows = db.execute(
        select(BorrowRecord, Equipment.name)
        .join(Equipment, BorrowRecord.equipment_id == Equipment.id)
        .order_by(BorrowRecord.id.desc())  # newest first
    ).all()
    results = [to_out(record, name) for record, name in rows]
    # Status is computed, so it is filtered here rather than in SQL. The
    # record count is small (one department), so this stays simple.
    if status:
        results = [item for item in results if item.status == status]
    return results


def return_borrow(db: Session, borrow_id: int) -> BorrowOut:
    record = get_by_id(db, BorrowRecord, borrow_id)
    if record is None:
        raise BorrowNotFoundError(borrow_id)
    if record.return_date is not None:
        raise AlreadyReturnedError(borrow_id)
    record.return_date = today_ph()
    db.commit()
    return to_out(record, record.equipment.name)


def to_out(record: BorrowRecord, equipment_name: str) -> BorrowOut:
    return BorrowOut(
        id=record.id,
        equipment_id=record.equipment_id,
        equipment_name=equipment_name,
        borrower_name=record.borrower_name,
        id_number=record.id_number,
        borrower_type=record.borrower_type,
        quantity=record.quantity,
        borrow_date=record.borrow_date,
        due_date=record.due_date,
        return_date=record.return_date,
        status=compute_status(record.due_date, record.return_date, today_ph()),
    )
