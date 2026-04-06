import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Child, Device, DeviceEnrollment, User
from backend.app.schemas.schemas import DeviceEnrollConsume, DeviceEnrollmentCreate, DeviceOut
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/enrollment")
def create_enrollment(payload: DeviceEnrollmentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.get(Child, payload.child_id)
    if not child or child.user_id != user.id:
        raise HTTPException(status_code=404, detail="child not found")
    code = secrets.token_urlsafe(16)
    enrollment = DeviceEnrollment(child_id=child.id, enrollment_code=code)
    db.add(enrollment)
    write_audit(db, user.id, "device.enrollment.create", "device_enrollment", enrollment.id)
    db.commit()
    return {"enrollment_id": enrollment.id, "enrollment_code": code}


@router.post("/enroll", response_model=DeviceOut)
def enroll(payload: DeviceEnrollConsume, db: Session = Depends(get_db)):
    enrollment = db.scalar(
        select(DeviceEnrollment).where(
            DeviceEnrollment.enrollment_code == payload.enrollment_code,
            DeviceEnrollment.consumed.is_(False),
            DeviceEnrollment.deleted_at.is_(None),
        )
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="invalid enrollment code")
    enrollment.consumed = True
    device = Device(child_id=enrollment.child_id, name=payload.name, platform=payload.platform)
    db.add(device)
    db.commit()
    db.refresh(device)
    return DeviceOut(id=device.id, child_id=device.child_id, name=device.name, platform=device.platform)


@router.get("", response_model=list[DeviceOut])
def list_devices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Device).join(Child, Child.id == Device.child_id).where(Child.user_id == user.id, Device.deleted_at.is_(None))
    ).scalars()
    return [DeviceOut(id=d.id, child_id=d.child_id, name=d.name, platform=d.platform) for d in rows]
