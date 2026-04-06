# ADR-0001: Kotlin Multiplatform + Compose Multiplatform

## Status
Accepted

## Decision
Use Kotlin Multiplatform for shared domain/networking and Compose Multiplatform for Android + desktop UI.

## Consequences
- Shared business logic across targets.
- Single API contract implementation in `client/shared`.
- Separate packaging pipeline for Android AAB and desktop installers.
