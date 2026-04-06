from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from threading import Lock
from uuid import uuid4

from app.models import Device, Event, EventType, Location, Role, Session, SessionStatus, User


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self.users: dict[str, User] = {}
        self.devices: dict[str, Device] = {}
        self.sessions: dict[str, Session] = {}
        self.locations: dict[str, list[Location]] = defaultdict(list)
        self.events: list[Event] = []

    def create_user(self, role: str) -> User:
        user = User(id=str(uuid4()), role=Role(role))
        with self._lock:
            self.users[user.id] = user
        return user

    def create_session(self, child_id: str) -> Session:
        session = Session(id=str(uuid4()), child_id=child_id)
        with self._lock:
            self.sessions[session.id] = session
            self.events.append(
                Event(
                    type=EventType.PANIC_TRIGGERED,
                    child_id=child_id,
                    session_id=session.id,
                    timestamp=datetime.utcnow(),
                    payload={},
                )
            )
        return session

    def close_session(self, session_id: str) -> Session:
        with self._lock:
            session = self.sessions[session_id]
            session.status = SessionStatus.RESOLVED
            session.end_time = datetime.utcnow()
            self.events.append(
                Event(
                    type=EventType.SESSION_END,
                    child_id=session.child_id,
                    session_id=session.id,
                    timestamp=datetime.utcnow(),
                    payload={},
                )
            )
        return session

    def add_location(self, location: Location) -> None:
        with self._lock:
            self.locations[location.session_id].append(location)
            session = self.sessions.get(location.session_id)
            if session is None:
                raise KeyError("session_not_found")
            self.events.append(
                Event(
                    type=EventType.LOCATION_UPDATE,
                    child_id=session.child_id,
                    session_id=location.session_id,
                    timestamp=location.timestamp,
                    payload={"lat": location.lat, "lng": location.lng, "accuracy": location.accuracy},
                )
            )

    def get_session_payload(self, session_id: str) -> dict:
        session = self.sessions[session_id]
        session_events = [e for e in self.events if e.session_id == session_id]
        return {
            "session": asdict(session),
            "locations": [asdict(l) for l in self.locations.get(session_id, [])],
            "events": [asdict(e) for e in session_events],
        }

    def get_child_sessions(self, child_id: str) -> list[Session]:
        return [s for s in self.sessions.values() if s.child_id == child_id]
