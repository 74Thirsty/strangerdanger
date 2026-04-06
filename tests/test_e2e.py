from fastapi.testclient import TestClient

from backend.app.main import app


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_onboarding_and_core_flows():
    client = TestClient(app)

    register = client.post(
        "/api/v1/auth/register",
        json={"email": "parent@example.com", "password": "S3curePasswd!", "household_name": "Home"},
    )
    assert register.status_code == 200
    tokens = register.json()
    access = tokens["access_token"]

    child = client.post("/api/v1/children", json={"name": "Ava"}, headers=_auth_header(access)).json()
    child_id = child["id"]

    enrollment = client.post(
        "/api/v1/devices/enrollment",
        json={"child_id": child_id},
        headers=_auth_header(access),
    )
    assert enrollment.status_code == 200
    code = enrollment.json()["enrollment_code"]

    device = client.post("/api/v1/devices/enroll", json={"enrollment_code": code, "name": "Pixel-1", "platform": "android"})
    assert device.status_code == 200
    device_id = device.json()["id"]

    session = client.post(
        "/api/v1/sessions",
        json={"child_id": child_id, "device_id": device_id},
        headers=_auth_header(access),
    )
    assert session.status_code == 200
    session_id = session.json()["id"]

    geofence = client.post(
        "/api/v1/geofences",
        json={
            "child_id": child_id,
            "name": "School",
            "center_latitude": 37.0,
            "center_longitude": -122.0,
            "radius_m": 400,
        },
        headers=_auth_header(access),
    )
    assert geofence.status_code == 200

    loc = client.post(
        "/api/v1/locations",
        json={
            "session_id": session_id,
            "latitude": 37.0,
            "longitude": -122.0,
            "accuracy_m": 9.0,
            "confidence": 90,
            "idempotency_key": "evt-1",
        },
        headers=_auth_header(access),
    )
    assert loc.status_code == 200

    panic = client.post(
        "/api/v1/panic",
        json={"child_id": child_id, "session_id": session_id, "notes": "help"},
        headers=_auth_header(access),
    )
    assert panic.status_code == 200

    alerts = client.get("/api/v1/alerts", headers=_auth_header(access))
    assert alerts.status_code == 200
    assert len(alerts.json()) >= 2
