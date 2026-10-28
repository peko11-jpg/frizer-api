from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # bitno: da Python "vidi" modele
from app.database import Base, engine
from app.routers import auth, bookings, services, stylists


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Frizer API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(stylists.router)
app.include_router(bookings.router)


@app.get("/health")
def health():
    return {"status": "ok"}