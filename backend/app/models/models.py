import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    household_name: Mapped[str] = mapped_column(String(255), default="default-household")


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Child(Base, TimestampMixin):
    __tablename__ = "children"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class DeviceEnrollment(Base, TimestampMixin):
    __tablename__ = "device_enrollments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    enrollment_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Device(Base, TimestampMixin):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(64), default="android")


class TrackingSession(Base, TimestampMixin):
    __tablename__ = "tracking_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LocationEvent(Base, TimestampMixin):
    __tablename__ = "location_events"
    __table_args__ = (UniqueConstraint("session_id", "idempotency_key", name="uq_location_idempotency"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("tracking_sessions.id", ondelete="CASCADE"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    accuracy_m: Mapped[float] = mapped_column(Float)
    confidence: Mapped[int] = mapped_column(Integer, default=100)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)


class Geofence(Base, TimestampMixin):
    __tablename__ = "geofences"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    center_latitude: Mapped[float] = mapped_column(Float)
    center_longitude: Mapped[float] = mapped_column(Float)
    radius_m: Mapped[float] = mapped_column(Float)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class GeofenceEvent(Base, TimestampMixin):
    __tablename__ = "geofence_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    geofence_id: Mapped[str] = mapped_column(ForeignKey("geofences.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("tracking_sessions.id", ondelete="CASCADE"), index=True)
    transition: Mapped[str] = mapped_column(String(16))


class PanicEvent(Base, TimestampMixin):
    __tablename__ = "panic_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("tracking_sessions.id", ondelete="CASCADE"), index=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class NotificationDelivery(Base, TimestampMixin):
    __tablename__ = "notification_deliveries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(32), default="in_app")
    status: Mapped[str] = mapped_column(String(32), default="pending")


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(128))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text, default="{}")


class PermissionStateSnapshot(Base, TimestampMixin):
    __tablename__ = "permission_state_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    location_granted: Mapped[bool] = mapped_column(Boolean, default=False)
    background_granted: Mapped[bool] = mapped_column(Boolean, default=False)


class DeviceHealthSnapshot(Base, TimestampMixin):
    __tablename__ = "device_health_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    battery_level: Mapped[int] = mapped_column(Integer)
    online: Mapped[bool] = mapped_column(Boolean, default=True)
