from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Alert, Child, PanicEvent, TrackingSession, User
from backend.app.schemas.schemas import PanicCreate
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/panic", tags=["panic"])


@router.post("")
def create_panic(payload: PanicCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.scalar(select(Child).where(Child.id == payload.child_id, Child.user_id == user.id))
    if not child:
        raise HTTPException(status_code=404, detail="child not found")
    session = db.get(TrackingSession, payload.session_id)
    if not session or session.child_id != child.id:
        raise HTTPException(status_code=404, detail="session not found")
    panic = PanicEvent(child_id=child.id, session_id=session.id, notes=payload.notes)
    db.add(panic)
    db.add(Alert(user_id=user.id, child_id=child.id, type="panic", payload=payload.notes or "panic triggered"))
    write_audit(db, user.id, "panic.create", "panic_event", panic.id)
    db.commit()
    db.refresh(panic)
    return {"id": panic.id, "created_at": panic.created_at}
