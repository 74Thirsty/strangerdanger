from fastapi.testclient import TestClient

from backend.app.main import app


def _header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_location_idempotency_rejects_duplicate():
    client = TestClient(app)
    reg = client.post("/api/v1/auth/register", json={"email": "idempo@example.com", "password": "VeryStrongPass1!", "household_name": "Home"})
    token = reg.json()["access_token"]
    child_id = client.post("/api/v1/children", json={"name": "Child"}, headers=_header(token)).json()["id"]
    code = client.post("/api/v1/devices/enrollment", json={"child_id": child_id}, headers=_header(token)).json()["enrollment_code"]
    device_id = client.post("/api/v1/devices/enroll", json={"enrollment_code": code, "name": "Tracker", "platform": "android"}).json()["id"]
    session_id = client.post("/api/v1/sessions", json={"child_id": child_id, "device_id": device_id}, headers=_header(token)).json()["id"]

    body = {
        "session_id": session_id,
        "latitude": 12.0,
        "longitude": 13.0,
        "accuracy_m": 8.0,
        "confidence": 80,
        "idempotency_key": "same-key",
    }
    first = client.post("/api/v1/locations", json=body, headers=_header(token))
    second = client.post("/api/v1/locations", json=body, headers=_header(token))
    assert first.status_code == 200
    assert second.status_code == 409
