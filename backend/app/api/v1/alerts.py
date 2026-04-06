from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Alert, User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Alert).where(Alert.user_id == user.id).order_by(Alert.created_at.desc())).all()
    return [{"id": r.id, "type": r.type, "payload": r.payload, "read": r.read, "created_at": r.created_at} for r in rows]


@router.post("/{alert_id}/read")
def mark_read(alert_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.scalar(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")
    alert.read = True
    db.commit()
    return {"ok": True}
