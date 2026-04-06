# Threat Model Summary

## Key Risks
- Token theft/replay.
- Unauthorized cross-household resource access.
- Location ingest flooding and replay.
- Notification fanout failures masking panic incidents.

## Mitigations Implemented
- JWT auth + hashed refresh tokens.
- Ownership checks on every mutating endpoint.
- Idempotency keys for location ingestion.
- Persistent audit events for sensitive actions.

## Remaining Hardening Tasks
- Redis-backed global rate limiting.
- Device-bound token proofs.
- Signed webhook notification channels.
