from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .timeutil import utcnow

CATEGORIES = ["Laptop", "Projector", "Camera", "Audio", "Networking", "Others"]
BORROWER_TYPES = ["Student", "Faculty"]


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    # Lowercased copy of name; the UNIQUE constraint here makes the
    # duplicate check case-insensitive even under concurrent requests.
    name_key: Mapped[str] = mapped_column(String(60), unique=True)
    category: Mapped[str] = mapped_column(String(20))
    total_quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    borrows: Mapped[list["BorrowRecord"]] = relationship(back_populates="equipment")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    borrower_name: Mapped[str] = mapped_column(String(100))
    id_number: Mapped[str] = mapped_column(String(20))
    borrower_type: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    borrow_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    # NULL until staff records the return. Status and availability are
    # derived from this, never stored.
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    equipment: Mapped[Equipment] = relationship(back_populates="borrows")
