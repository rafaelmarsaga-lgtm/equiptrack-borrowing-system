from sqlalchemy.orm import Session

from ..models import BorrowRecord, Equipment
from ..schemas import BorrowCreate, BorrowOut
from ..timeutil import today_ph
from .equipment_service import available_quantity


class EquipmentNotFoundError(Exception):
    """The requested equipment id does not exist."""


class NotEnoughStockError(Exception):
    def __init__(self, available: int, requested: int):
        self.available = available
        self.requested = requested
        super().__init__(f"Only {available} available; you asked for {requested}.")


def create_borrow(db: Session, data: BorrowCreate) -> BorrowOut:
    equipment = db.get(Equipment, data.equipment_id)
    if equipment is None:
        raise EquipmentNotFoundError(data.equipment_id)

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
    )
