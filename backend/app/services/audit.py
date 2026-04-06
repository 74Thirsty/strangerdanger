from sqlalchemy.orm import Session

from backend.app.models.models import AuditEvent


def write_audit(db: Session, user_id: str, action: str, resource_type: str, resource_id: str, details: str = "{}") -> None:
    db.add(
        AuditEvent(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
    )
