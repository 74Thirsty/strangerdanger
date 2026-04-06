from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import AuditEvent, User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AuditEvent).where(AuditEvent.user_id == user.id).order_by(AuditEvent.created_at.desc()).limit(200)).all()
    return [
        {
            "id": row.id,
            "action": row.action,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "details": row.details,
            "created_at": row.created_at,
        }
        for row in rows
    ]
