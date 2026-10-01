"""Fill the local database with sample equipment. Safe to run more than once:
items whose name already exists are skipped.

Run from the backend folder:  python seed_data.py
"""
from app import models  # noqa: F401  (registers the tables on Base)
from app.database import Base, SessionLocal, engine
from app.services.equipment_service import DuplicateEquipmentError, create_equipment

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


if __name__ == "__main__":
    seed()
