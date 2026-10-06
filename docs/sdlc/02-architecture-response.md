# Stage 2 Response — Architecture

## Summary

Proposed a simple **Flask** Python web architecture for Jira **KAN-1 (Search flight)**: anonymous Jinja2 search UI, in-process validator, and in-memory JSON dummy catalog. No booking, no live airline APIs, no authentication. Stage 7 Playwright E2E is planned against stable `data-testid` contracts on GET `/` and POST `/search`. This stage writes design docs only (no application code).

## Artifacts

| Artifact | Path |
|----------|------|
| Primary | `architecture.md` |
| Stage response | `docs/sdlc/02-architecture-response.md` |

## Key Decisions

- **Framework: Flask** (not FastAPI, not Django) — smallest SSR HTML form + results stack for Playwright
- Dummy flights stored in **JSON loaded at startup** (not SQLite, not a live API)
- **POST `/search`** after **GET `/`** form; validation errors re-render without querying
- Passengers 1–9 remain **display-only**; match on case-insensitive cities + exact travel date
- Playwright Stage 7 scripts reserved under `tests/e2e/` using documented `data-testid`s
- CSRF via env `SECRET_KEY` if Flask-WTF is used; never commit `api-conf.properties`

## Open Questions / Blockers

- None that block Architecture approval
- Implementation details (exact JSON filenames, Flask-WTF vs bare forms) can be confirmed in Design Review after human approval

## PR

- **URL:** https://github.com/rkumar802212/CursorSdlc/pull/2
- **Title:** `[SDLC Stage 2] Architecture — KAN-1 Search flight (Flask)`
- **Branch:** `sdlc/stage-2-architecture-kan-1` → `main`

## Ready for Human Approval

**Yes.** Please review `architecture.md` (Flask choice, dummy JSON catalog, Playwright test-id contract) and the Stage 2 PR. Reply **approved** / **proceed to design review** (or request changes) before Stage 3. Do not start Design Review or implementation until then.
