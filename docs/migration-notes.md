# Migration Notes

Prototype in-memory assumptions were removed.
All lifecycle entities now persist via SQLAlchemy models.
`/locations` requires an authenticated user, active session, and ownership checks.
