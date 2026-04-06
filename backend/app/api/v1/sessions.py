from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Child, Device, TrackingSession, User
from backend.app.schemas.schemas import SessionCreate, SessionOut
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut)
def create_session(payload: SessionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.get(Child, payload.child_id)
    if not child or child.user_id != user.id:
        raise HTTPException(status_code=404, detail="child not found")
    device = db.get(Device, payload.device_id)
    if not device or device.child_id != child.id:
        raise HTTPException(status_code=404, detail="device not found")
    existing = db.scalar(select(TrackingSession).where(TrackingSession.device_id == device.id, TrackingSession.active.is_(True)))
    if existing:
        raise HTTPException(status_code=409, detail="device already has active session")
    session = TrackingSession(child_id=child.id, device_id=device.id, active=True)
    db.add(session)
    write_audit(db, user.id, "session.create", "tracking_session", session.id)
    db.commit()
    db.refresh(session)
    return SessionOut(id=session.id, child_id=session.child_id, device_id=session.device_id, active=session.active)


@router.post("/{session_id}/stop")
def stop_session(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.scalar(
        select(TrackingSession).join(Child, Child.id == TrackingSession.child_id).where(TrackingSession.id == session_id, Child.user_id == user.id)
    )
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    session.active = False
    session.ended_at = datetime.now(timezone.utc)
    write_audit(db, user.id, "session.stop", "tracking_session", session.id)
    db.commit()
    return {"ok": True}
