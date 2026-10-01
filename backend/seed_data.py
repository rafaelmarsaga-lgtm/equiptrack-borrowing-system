"""Fill the local database with sample equipment. Safe to run more than once:
items whose name already exists are skipped.

Run from the backend folder:  python seed_data.py
"""
from datetime import timedelta

from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine
from app.services.equipment_service import DuplicateEquipmentError, create_equipment
from app.timeutil import today_ph

SAMPLE_EQUIPMENT = [
    ("Dell Latitude laptop", "Laptop", 10),
    ("MacBook Air", "Laptop", 4),
    ("Epson projector", "Projector", 5),
    ("Canon DSLR camera", "Camera", 3),
    ("Portable speaker", "Audio", 6),
    ("Wireless microphone", "Audio", 8),
    ("Cisco router", "Networking", 2),
    ("HDMI cable", "Others", 20),
]


def seed_overdue_record(db) -> bool:
    """Add one past-due borrow so the Overdue status can be demonstrated.

    This is inserted directly through the ORM as HISTORICAL data on purpose:
    the API rejects due dates in the past, so it can't create this record.
    Dates are relative to today so it is overdue whenever the seed is run.
    Skipped if any borrow records already exist, so reruns don't add more.
    """
    if db.scalar(select(models.BorrowRecord.id).limit(1)) is not None:
        return False
    projector = db.scalar(select(models.Equipment).where(models.Equipment.name_key == "epson projector"))
    if projector is None:
        return False
    today = today_ph()
    db.add(models.BorrowRecord(
        equipment_id=projector.id,
        borrower_name="Dr. Jose Reyes",
        id_number="F-0045",
        borrower_type="Faculty",
        quantity=1,
        borrow_date=today - timedelta(days=10),
        due_date=today - timedelta(days=3),
        return_date=None,
    ))
    db.commit()
    return True


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        added = 0
        for name, category, total in SAMPLE_EQUIPMENT:
            try:
                create_equipment(db, name, category, total)
                added += 1
            except DuplicateEquipmentError:
                pass
        print(f"Seeded {added} new item(s); {len(SAMPLE_EQUIPMENT) - added} already existed.")
        if seed_overdue_record(db):
            print("Added 1 past-due borrow record (Epson projector).")


if __name__ == "__main__":
    seed()
