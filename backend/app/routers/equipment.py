from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import EquipmentCreate, EquipmentOut
from ..services import equipment_service

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentOut])
def list_equipment(search: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    return equipment_service.list_equipment(db, search, category)


@router.post("", response_model=EquipmentOut, status_code=201)
def add_equipment(data: EquipmentCreate, db: Session = Depends(get_db)):
    try:
        return equipment_service.create_equipment(db, data.name, data.category, data.total_quantity)
    except equipment_service.DuplicateEquipmentError:
        raise HTTPException(status_code=409, detail="That equipment already exists.")
