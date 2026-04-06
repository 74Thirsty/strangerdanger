from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
from backend.app.models.models import Child, Device, TrackingSession, User
from backend.app.core.security import hash_password

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    user = User(email="demo@local", password_hash=hash_password("DemoPassword123!"), household_name="Demo")
    db.add(user)
    db.flush()
    child = Child(user_id=user.id, name="Demo Child")
    db.add(child)
    db.flush()
    device = Device(child_id=child.id, name="Demo Android", platform="android")
    db.add(device)
    db.flush()
    session = TrackingSession(child_id=child.id, device_id=device.id, active=True)
    db.add(session)
    db.commit()
    print({"user_id": user.id, "child_id": child.id, "device_id": device.id, "session_id": session.id})
