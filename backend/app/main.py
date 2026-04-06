from fastapi import FastAPI

from backend.app.api.v1 import admin, alerts, audit, auth, children, devices, geofences, locations, panic, sessions
from backend.app.db.base import Base
from backend.app.db.session import engine

app = FastAPI(title="strangerdanger", version="1.0.0")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(children.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(geofences.router, prefix="/api/v1")
app.include_router(panic.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}
