<<<<<<< ours
# Stranger Danger MVP

Backend-first MVP implementing the requested two-layer alert system:

1. **Hard triggers** (`panic_triggered`, tamper-after-anomaly) that immediately escalate to `CRITICAL`.
2. **Probabilistic score** + risk state machine (`NORMAL -> WATCH -> ELEVATED -> HIGH -> CRITICAL`) with hysteresis.

## Implemented APIs

- `POST /auth/register`
- `POST /auth/login`
- `POST /panic`
- `POST /location`
- `GET /children`
- `GET /session/{id}`
- `POST /geofence`
- `GET ws://.../ws/session/{id}`

## Event model

The backend emits and stores:

- `PANIC_TRIGGERED`
- `LOCATION_UPDATE`
- `GEOFENCE_EXIT`
- `CHECKIN_MISSED`
- `SESSION_END`

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.server:app --reload
```

## Test

```bash
pytest -q
```

## Notes

- Storage is in-memory for MVP iteration speed.
- Risk scoring in `app/risk.py` is deterministic and explainable.
- WebSocket channel shape is `session:{id}` via `/ws/session/{id}` endpoint.
=======
# strangerdanger

Production-oriented monorepo for family safety tracking with:
- FastAPI backend (`backend`)
- Kotlin Multiplatform + Compose client (`client`)
- infra manifests (`infra`)
- docs/runbooks (`docs`)
- test suite (`tests`)

## Quick start

```bash
docker compose -f infra/docker-compose.yml up -d
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Open API docs at `http://localhost:8000/docs` for inspection only (not required by clients).

## Backend production properties
- JWT access + hashed refresh tokens
- ownership-enforced child/device/session lifecycle
- idempotent location ingest keyed by `(session_id,idempotency_key)`
- geofence transition detection with exact state-transition alerts
- durable panic events + alert fanout records
- audit trail for sensitive operations

## Test

```bash
pytest -q
```

## Seed demo data

```bash
python scripts/seed_demo.py
```

## API base
`/api/v1`

See `docs/api.md` for endpoint list and `docs/architecture.md` for system architecture.
>>>>>>> theirs
