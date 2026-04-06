from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import (
    Alert,
    Child,
    Geofence,
    GeofenceEvent,
    LocationEvent,
    TrackingSession,
    User,
)
from backend.app.schemas.schemas import LocationIngest
from backend.app.services.audit import write_audit
from backend.app.services.geofence import haversine_m

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("")
def ingest_location(payload: LocationIngest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.scalar(
        select(TrackingSession)
        .join(Child, Child.id == TrackingSession.child_id)
        .where(TrackingSession.id == payload.session_id, TrackingSession.active.is_(True), Child.user_id == user.id)
    )
    if not session:
        raise HTTPException(status_code=404, detail="active session not found")

    event = LocationEvent(
        session_id=session.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        accuracy_m=payload.accuracy_m,
        confidence=payload.confidence,
        idempotency_key=payload.idempotency_key,
    )
    db.add(event)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="duplicate location idempotency key") from exc

    geofences = db.scalars(select(Geofence).where(Geofence.child_id == session.child_id, Geofence.enabled.is_(True))).all()
    for fence in geofences:
        dist = haversine_m(payload.latitude, payload.longitude, fence.center_latitude, fence.center_longitude)
        inside = dist <= fence.radius_m
        prior = db.scalar(
            select(GeofenceEvent)
            .where(GeofenceEvent.geofence_id == fence.id, GeofenceEvent.session_id == session.id)
            .order_by(GeofenceEvent.created_at.desc())
        )
        prev_state = prior.transition == "enter" if prior else None
        if prev_state is None or prev_state != inside:
            transition = "enter" if inside else "exit"
            gf_event = GeofenceEvent(geofence_id=fence.id, session_id=session.id, transition=transition)
            db.add(gf_event)
            db.add(
                Alert(
                    user_id=user.id,
                    child_id=session.child_id,
                    type=f"geofence_{transition}",
                    payload=f"{fence.name}:{transition}",
                )
            )
    write_audit(db, user.id, "location.ingest", "tracking_session", session.id)
    db.commit()
    return {"ok": True, "location_event_id": event.id}


@router.get("/status/{child_id}")
def child_status(child_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.scalar(select(Child).where(Child.id == child_id, Child.user_id == user.id))
    if not child:
        raise HTTPException(status_code=404, detail="child not found")
    session = db.scalar(
        select(TrackingSession)
        .where(TrackingSession.child_id == child.id)
        .order_by(TrackingSession.created_at.desc())
    )
    latest = None
    if session:
        latest = db.scalar(
            select(LocationEvent).where(LocationEvent.session_id == session.id).order_by(LocationEvent.created_at.desc())
        )
    return {
        "child_id": child.id,
        "session_id": session.id if session else None,
        "active": session.active if session else False,
        "latest_location": {
            "latitude": latest.latitude,
            "longitude": latest.longitude,
            "confidence": latest.confidence,
            "created_at": latest.created_at,
        }
        if latest
        else None,
    }
