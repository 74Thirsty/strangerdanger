from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Role(str, Enum):
    CHILD = "child"
    GUARDIAN = "guardian"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"


class RiskState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventType(str, Enum):
    PANIC_TRIGGERED = "PANIC_TRIGGERED"
    LOCATION_UPDATE = "LOCATION_UPDATE"
    GEOFENCE_EXIT = "GEOFENCE_EXIT"
    CHECKIN_MISSED = "CHECKIN_MISSED"
    SESSION_END = "SESSION_END"
    TAMPER = "TAMPER"


@dataclass(slots=True)
class User:
    id: str
    role: Role


@dataclass(slots=True)
class Device:
    id: str
    user_id: str
    battery_level: int = 100
    last_seen: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class Session:
    id: str
    child_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    risk_level: RiskState = RiskState.CRITICAL


@dataclass(slots=True)
class Location:
    session_id: str
    lat: float
    lng: float
    timestamp: datetime
    accuracy: float


@dataclass(slots=True)
class Event:
    type: EventType
    child_id: str
    session_id: str | None
    timestamp: datetime
    payload: dict[str, Any]
