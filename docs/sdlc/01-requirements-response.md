# Stage 1 Response — Requirements

## Summary

Captured functional and non-functional requirements for Jira **KAN-1 (Search flight)**: an anonymous Python web app that searches dummy/mock flights by departure city, arrival city, travel date, and passenger count. Clarifying questions were closed by human **Approved** with documented sensible defaults.

## Artifacts

| Artifact | Path |
|----------|------|
| Primary | `requirements.md` |
| Stage response | `docs/sdlc/01-requirements-response.md` |
| Supporting (repo bootstrap) | `.gitignore`, `README.md`, `api-conf.properties.example` |

## Key Decisions

- Dummy/mock search only; booking, payment, seat selection, and real airline APIs are out of scope
- Free-text cities; case-insensitive exact match on departure city + arrival city + travel date
- Passengers integer 1–9, display-only (no inventory/price impact)
- Past dates blocked; same departure/arrival cities rejected; empty results show “No flights found”
- Anonymous public search (no login)
- Delivery: Python web application; Playwright E2E in Verify; framework choice deferred to Architecture

## Open Questions / Blockers

- None for Stage 1
- Framework and dummy-data storage shape deferred to Stage 2 (Architecture)

## PR

- **URL:** https://github.com/rkumar802212/CursorSdlc/pull/1
- **Title:** `[SDLC Stage 1] Requirements — KAN-1 Search flight`
- **Branch:** `sdlc/stage-1-requirements-kan-1` → `main`

## Ready for Human Approval

**Yes.** Please review `requirements.md` and the Stage 1 PR, then reply **approved** / **proceed to architecture** (or request changes) before Stage 2 begins.

### Security note

No secrets were written into requirements or this response. `api-conf.properties` is gitignored and was verified absent from the PR branch.
