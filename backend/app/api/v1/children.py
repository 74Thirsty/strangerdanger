from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.models import Child, User
from backend.app.schemas.schemas import ChildCreate, ChildOut
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/children", tags=["children"])


@router.post("", response_model=ChildOut)
def create_child(payload: ChildCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = Child(user_id=user.id, name=payload.name)
    db.add(child)
    write_audit(db, user.id, "child.create", "child", child.id)
    db.commit()
    db.refresh(child)
    return ChildOut(id=child.id, name=child.name, created_at=child.created_at)


@router.get("", response_model=list[ChildOut])
def list_children(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Child).where(Child.user_id == user.id, Child.deleted_at.is_(None))).all()
    return [ChildOut(id=row.id, name=row.name, created_at=row.created_at) for row in rows]


@router.delete("/{child_id}")
def delete_child(child_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = db.get(Child, child_id)
    if not child or child.user_id != user.id:
        raise HTTPException(status_code=404, detail="child not found")
    child.deleted_at = child.updated_at
    write_audit(db, user.id, "child.delete", "child", child.id)
    db.commit()
    return {"ok": True}
