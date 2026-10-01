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
    except borrow_service.DueDateOutOfRangeError:
        raise HTTPException(status_code=400, detail="Due date must be between today and 14 days from today.")
    except borrow_service.NotEnoughStockError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("", response_model=list[BorrowOut])
def list_borrows(status: str | None = None, db: Session = Depends(get_db)):
    return borrow_service.list_borrows(db, status)


@router.post("/{borrow_id}/return", response_model=BorrowOut)
def return_equipment(borrow_id: int, db: Session = Depends(get_db)):
    try:
        return borrow_service.return_borrow(db, borrow_id)
    except borrow_service.BorrowNotFoundError:
        raise HTTPException(status_code=404, detail="Borrow record not found.")
    except borrow_service.AlreadyReturnedError:
        raise HTTPException(status_code=400, detail="This item was already returned.")
