# Operational Runbook

## Health Checks
- `GET /healthz` liveness.
- `GET /readyz` readiness.

## Incident: Location Ingestion Latency
1. Check DB saturation and lock contention.
2. Verify active sessions and idempotency conflict rate.
3. Drain retry queues for downstream notification channels.

## Incident: Auth Failures Spike
1. Verify JWT signing secret rotation status.
2. Inspect login audit events and source IP patterns.
3. Trigger temporary rate-limit tightening.
