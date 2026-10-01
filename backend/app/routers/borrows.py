from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import BorrowCreate, BorrowOut
from ..services import borrow_service

router = APIRouter(prefix="/api/borrows", tags=["borrows"])


@router.post("", response_model=BorrowOut, status_code=201)
def record_borrow(data: BorrowCreate, db: Session = Depends(get_db)):
    try:
        return borrow_service.create_borrow(db, data)
    except borrow_service.EquipmentNotFoundError:
        raise HTTPException(status_code=404, detail="Equipment not found.")
    except borrow_service.NotEnoughStockError as error:
        raise HTTPException(status_code=400, detail=str(error))
