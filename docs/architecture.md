# StrangerDanger Architecture

## Monorepo Layout
- `backend`: FastAPI API under `/api/v1` with SQLAlchemy persistence.
- `client`: Kotlin Multiplatform + Compose Multiplatform targets for Android and desktop.
- `infra`: Local infrastructure manifests (PostgreSQL + Redis compose stack).
- `scripts`: Bootstrap and demo seed utilities.
- `tests`: API integration and E2E tests.

## Backend Modules
Bounded modules are implemented as routers:
- auth
- children
- devices
- sessions
- locations
- geofences
- alerts
- panic
- admin
- audit

## Runtime Notes
- Production database: PostgreSQL (`DATABASE_URL`).
- Local default database: SQLite file for zero-friction bring-up.
- JWT access/refresh token model with refresh token revocation.
- Idempotency for location ingest via `(session_id, idempotency_key)` unique constraint.
