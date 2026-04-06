# Deployment

## Local
1. `docker compose -f infra/docker-compose.yml up -d`
2. `pip install -r backend/requirements.txt`
3. `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`

## Staging/Production
- Build backend container from repository root.
- Run with `uvicorn backend.app.main:app --workers 4 --host 0.0.0.0 --port 8000`.
- Inject `DATABASE_URL`, `JWT_SECRET`, and environment-specific values via secret manager.
