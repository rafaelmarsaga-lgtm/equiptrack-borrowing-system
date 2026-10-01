from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import models  # noqa: F401  (registers the tables on Base)
from .database import Base, engine
from .routers import equipment

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup; cheap and idempotent for SQLite.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="EquipTrack", lifespan=lifespan)
app.include_router(equipment.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Mounted last so /api/* routes win. One origin means no CORS to configure.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
