from fastapi import FastAPI

from app.routers import auth, bookings, services, stylists, users

app = FastAPI(title="Frizer API")

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(stylists.router)
app.include_router(bookings.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}