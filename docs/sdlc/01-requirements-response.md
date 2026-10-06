# Stage 1 Response â€” Requirements

## Stage

- **Stage:** 1 â€” Requirements
- **Jira:** KAN-1 (Search flight)
- **Status:** Complete â€” awaiting human approval before Stage 2 (Architecture)

## Summary

Captured functional and non-functional requirements for an anonymous flight-search Python web app that queries dummy/mock flights. Clarifying questions were answered via human â€œApprovedâ€ with documented sensible defaults (scope, result fields, matching, passengers, dates, auth, UX, delivery).

## Artifacts

| Artifact | Path |
|----------|------|
| Primary | `requirements.md` |
| Stage response | `docs/sdlc/01-requirements-response.md` |

## Decisions locked in Stage 1

- Dummy/mock search only; no booking/payment/real airline APIs
- Free-text cities; case-insensitive exact match on cities + date
- Passengers 1â€“9 display-only; past dates blocked; anonymous access
- Python web app + Playwright E2E in Verify; framework deferred to Architecture

## Security

- No secrets, tokens, or credentials written into requirements or this response
- `api-conf.properties` remains local-only and must not be committed

## PR

- **URL:** _pending â€” will be updated when Stage 1 PR is opened_
- **Title pattern:** `[SDLC Stage 1] Requirements â€” KAN-1 Search flight`

## Human approval gate

Please review `requirements.md` and reply **approved** / **proceed to architecture** (or request changes) before Stage 2 begins.
