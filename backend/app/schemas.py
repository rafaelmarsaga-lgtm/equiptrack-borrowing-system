from datetime import date

from pydantic import BaseModel


class EquipmentCreate(BaseModel):
    # Only types are checked here; full rules (lengths, ranges, categories)
    # are added in Step 6.
    name: str
    category: str
    total_quantity: int


class EquipmentOut(BaseModel):
    id: int
    name: str
    category: str
    total_quantity: int
    available: int  # computed on every read, never stored


class BorrowCreate(BaseModel):
    # Types only for now; field rules (lengths, ID format, due-date window)
    # are added in Step 6.
    borrower_name: str
    id_number: str
    borrower_type: str
    equipment_id: int
    quantity: int
    due_date: date


class BorrowOut(BaseModel):
    id: int
    equipment_id: int
    equipment_name: str
    borrower_name: str
    id_number: str
    borrower_type: str
    quantity: int
    borrow_date: date
    due_date: date
    return_date: date | None
    status: str  # Borrowed / Returned / Overdue, computed on every read
