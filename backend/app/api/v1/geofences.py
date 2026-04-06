from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Child, Geofence, User
from backend.app.schemas.schemas import GeofenceCreate
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/geofences", tags=["geofences"])


@router.post("")
def create_geofence(payload: GeofenceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.get(Child, payload.child_id)
    if not child or child.user_id != user.id:
        raise HTTPException(status_code=404, detail="child not found")
    geofence = Geofence(**payload.model_dump())
    db.add(geofence)
    write_audit(db, user.id, "geofence.create", "geofence", geofence.id)
    db.commit()
    db.refresh(geofence)
    return {"id": geofence.id}


@router.get("/{child_id}")
def list_geofences(child_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.get(Child, child_id)
    if not child or child.user_id != user.id:
        raise HTTPException(status_code=404, detail="child not found")
    rows = db.scalars(select(Geofence).where(Geofence.child_id == child_id, Geofence.deleted_at.is_(None))).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "radius_m": row.radius_m,
            "enabled": row.enabled,
        }
        for row in rows
    ]
