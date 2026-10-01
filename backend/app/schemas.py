from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

# Whitespace is trimmed BEFORE the length check, so "   " counts as empty.
EquipmentName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=60)]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
IdNumber = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[A-Za-z0-9-]{4,20}$")]
Category = Literal["Laptop", "Projector", "Camera", "Audio", "Networking", "Others"]
BorrowerType = Literal["Student", "Faculty"]


class EquipmentCreate(BaseModel):
    name: EquipmentName
    category: Category
    total_quantity: int = Field(ge=1, le=100)


class EquipmentOut(BaseModel):
    id: int
    name: str
    category: str
    total_quantity: int
    available: int  # computed on every read, never stored


class BorrowCreate(BaseModel):
    # The due-date WINDOW (today to +14 days) is a business rule checked in the
    # service, because it depends on today's date.
    borrower_name: FullName
    id_number: IdNumber
    borrower_type: BorrowerType
    equipment_id: int
    quantity: int = Field(ge=1)
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
