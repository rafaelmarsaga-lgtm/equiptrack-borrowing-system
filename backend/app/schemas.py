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
