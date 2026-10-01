from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import BorrowRecord, Equipment
from ..schemas import EquipmentOut

LIKE_ESCAPE = "\\"


class DuplicateEquipmentError(Exception):
    """An item with the same name (ignoring case) already exists."""


def escape_like(text: str) -> str:
    """Make user text safe inside LIKE: % and _ are wildcards, so they must
    match literally. The escape character is escaped first."""
    return (
        text.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", LIKE_ESCAPE + "%")
        .replace("_", LIKE_ESCAPE + "_")
    )


def _borrowed_by_equipment():
    """Subquery: quantity currently out (not yet returned) per equipment."""
    return (
        select(
            BorrowRecord.equipment_id.label("equipment_id"),
            func.sum(BorrowRecord.quantity).label("borrowed"),
        )
        .where(BorrowRecord.return_date.is_(None))
        .group_by(BorrowRecord.equipment_id)
        .subquery()
    )


def available_quantity(db: Session, equipment_id: int) -> int:
    """total - quantity of unreturned borrows. Computed, never stored."""
    equipment = db.get(Equipment, equipment_id)
    borrowed = db.scalar(
        select(func.coalesce(func.sum(BorrowRecord.quantity), 0)).where(
            BorrowRecord.equipment_id == equipment_id,
            BorrowRecord.return_date.is_(None),
        )
    )
    return equipment.total_quantity - borrowed


def list_equipment(db: Session, search: str | None = None, category: str | None = None) -> list[EquipmentOut]:
    borrowed = _borrowed_by_equipment()
    query = select(Equipment, func.coalesce(borrowed.c.borrowed, 0)).outerjoin(
        borrowed, borrowed.c.equipment_id == Equipment.id
    )
    if search and search.strip():
        pattern = f"%{escape_like(search.strip().lower())}%"
        query = query.where(Equipment.name_key.like(pattern, escape=LIKE_ESCAPE))
    if category:
        query = query.where(Equipment.category == category)
    rows = db.execute(query.order_by(Equipment.name_key)).all()
    return [to_out(equipment, qty_borrowed) for equipment, qty_borrowed in rows]


def create_equipment(db: Session, name: str, category: str, total_quantity: int) -> EquipmentOut:
    name = name.strip()
    key = name.lower()
    # Check first for a clean message; the UNIQUE column is the safety net
    # if two requests race.
    if db.scalar(select(Equipment.id).where(Equipment.name_key == key)) is not None:
        raise DuplicateEquipmentError(name)
    equipment = Equipment(name=name, name_key=key, category=category, total_quantity=total_quantity)
    db.add(equipment)
    db.commit()
    return to_out(equipment, 0)


def to_out(equipment: Equipment, borrowed: int) -> EquipmentOut:
    return EquipmentOut(
        id=equipment.id,
        name=equipment.name,
        category=equipment.category,
        total_quantity=equipment.total_quantity,
        available=equipment.total_quantity - borrowed,
    )
