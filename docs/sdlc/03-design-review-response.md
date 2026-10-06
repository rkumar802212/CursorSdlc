# Stage 3 Response — Design Review

## Summary

Completed a rigorous Design Review of the approved Flask architecture for **KAN-1 (Search flight)** against `requirements.md`. Flask + Jinja2 + in-memory JSON remains fit for purpose. One **critical** Playwright contract defect (duplicate `data-testid`s) and several **warnings** (trim/normalize, CSRF, GET `/search`, frozen fixtures, `server-today`, fail-fast catalog, debug off) were closed with **minimal updates to `architecture.md`**. No production implementation code was written. Stage 4 Implementation Planning must not start until a human accepts this review.

## Artifacts

| Artifact | Path |
|----------|------|
| Primary | `design-review.md` |
| Architecture (updated) | `architecture.md` |
| Stage response | `docs/sdlc/03-design-review-response.md` |

## Key Decisions

- Keep Flask; do not switch stacks.
- Namespace result card test ids as `result-*`; publish a DOM state matrix for Playwright.
- Shared `normalize_city` (trim + casefold); whitespace-only = missing.
- Flask-WTF CSRF **required**; GET `/search` **302 → `/`**.
- Seeded fixtures: `Delhi`→`Mumbai` on `2099-06-15`; zero match `Delhi`+`Kolkata`+`2099-12-31`.
- Expose `server-today` for E2E past-date math; fail-fast if `flights.json` is missing; `debug=False`.
- Approval Status: **pending human acceptance**.

## Open Questions / Blockers

- **Blocker:** Human must accept `design-review.md` (findings + architecture updates) before Stage 4.
- No unresolved product questions from Stage 1; remaining items are residual MVP risks (single process, POST refresh), not open requirements.

## PR

- **URL:** pending
- **Title:** `[SDLC Stage 3] Design Review — KAN-1 Search flight`
- **Branch:** `sdlc/stage-3-design-review-kan-1` → `main`

## Ready for Human Approval

**Yes.** Please review `design-review.md` and the architecture updates in `architecture.md`, then the Stage 3 PR. Reply **approved** / **accept design review** (or request changes) before Implementation Planning. Do not start Stage 4 or write application code until then.
