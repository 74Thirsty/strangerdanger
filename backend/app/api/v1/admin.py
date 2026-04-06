from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Alert, LocationEvent, PanicEvent, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/diagnostics")
def diagnostics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "user_id": user.id,
        "panic_count": db.scalar(select(func.count()).select_from(PanicEvent)),
        "ingestion_count": db.scalar(select(func.count()).select_from(LocationEvent)),
        "alert_count": db.scalar(select(func.count()).select_from(Alert)),
    }
