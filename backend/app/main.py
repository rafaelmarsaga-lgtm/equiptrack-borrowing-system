from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from . import models  # noqa: F401  (registers the tables on Base)
from .database import Base, engine
from .errors import validation_error_handler
from .routers import borrows, equipment

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup; cheap and idempotent for SQLite.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="EquipTrack", lifespan=lifespan)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(equipment.router)
app.include_router(borrows.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Mounted last so /api/* routes win. One origin means no CORS to configure.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
