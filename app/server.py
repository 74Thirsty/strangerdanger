from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.models import Location
from app.risk import compute_risk
from app.store import InMemoryStore

app = FastAPI(title="Stranger Danger MVP")
store = InMemoryStore()
ws_connections: dict[str, list[WebSocket]] = {}


class RegisterRequest(BaseModel):
    role: str = Field(pattern="^(child|guardian)$")


class PanicRequest(BaseModel):
    child_id: str


class LocationRequest(BaseModel):
    session_id: str
    lat: float
    lng: float
    timestamp: datetime
    accuracy: float = Field(ge=0)
    features: dict[str, float | bool] = Field(default_factory=dict)
    quality: dict[str, float] = Field(default_factory=dict)


class GeofenceRequest(BaseModel):
    child_id: str
    name: str
    center_lat: float
    center_lng: float
    radius_m: float


@app.post("/auth/register")
def register(req: RegisterRequest) -> dict[str, str]:
    user = store.create_user(req.role)
    return {"user_id": user.id, "role": user.role.value}


@app.post("/auth/login")
def login() -> dict[str, str]:
    return {"token": "dev-token"}


@app.post("/panic")
async def panic(req: PanicRequest) -> dict[str, Any]:
    session = store.create_session(req.child_id)
    await _broadcast(
        session.id,
        {
            "event": "PANIC_TRIGGERED",
            "session_id": session.id,
            "child_id": req.child_id,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_state": "CRITICAL",
        },
    )
    return {"session_id": session.id, "status": session.status.value}


@app.post("/location")
async def location(req: LocationRequest) -> dict[str, Any]:
    try:
        session = store.sessions[req.session_id]
    except KeyError as exc:
        raise HTTPException(404, detail="session_not_found") from exc

    prev = session.risk_level
    risk_score, risk_state = compute_risk(req.features, req.quality, prev)
    session.risk_level = risk_state

    loc = Location(
        session_id=req.session_id,
        lat=req.lat,
        lng=req.lng,
        timestamp=req.timestamp,
        accuracy=req.accuracy,
    )
    store.add_location(loc)

    payload = {
        "event": "LOCATION_UPDATE",
        "session_id": req.session_id,
        "lat": req.lat,
        "lng": req.lng,
        "timestamp": req.timestamp.isoformat(),
        "risk_score": risk_score,
        "risk_state": risk_state.value,
    }
    await _broadcast(req.session_id, payload)
    return payload


@app.get("/children")
def children() -> dict[str, Any]:
    children_ids = [u.id for u in store.users.values() if u.role.value == "child"]
    return {"children": [{"child_id": cid, "sessions": [s.id for s in store.get_child_sessions(cid)]} for cid in children_ids]}


@app.get("/session/{session_id}")
def session(session_id: str) -> dict[str, Any]:
    try:
        return store.get_session_payload(session_id)
    except KeyError as exc:
        raise HTTPException(404, detail="session_not_found") from exc


@app.post("/geofence")
def geofence(req: GeofenceRequest) -> dict[str, Any]:
    return {"status": "saved", "child_id": req.child_id, "zone": req.model_dump()}


@app.websocket("/ws/session/{session_id}")
async def session_ws(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    ws_connections.setdefault(session_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[session_id].remove(websocket)


async def _broadcast(session_id: str, payload: dict[str, Any]) -> None:
    clients = ws_connections.get(session_id, [])
    stale: list[WebSocket] = []
    for client in clients:
        try:
            await client.send_json(payload)
        except RuntimeError:
            stale.append(client)

    for client in stale:
        clients.remove(client)
