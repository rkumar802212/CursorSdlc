# Stage 6 Response — Code Review

## Summary

Completed **Agentic SDLC Stage 6** peer review of the KAN-1 Flask search app. Evaluated every capstone checklist area. Found **1 critical** defect (invalid passenger input could 500) and several warnings; **fixed the critical item plus dependency/test gaps** in the Flask app and pytest suite. **pytest: 34 passed.** Ready for Verify is **yes**. Stage 7 Playwright MCP was **not** started.

## Artifacts

| Artifact | Path |
|----------|------|
| Code review (skill template) | `docs/sdlc/06-code-review.md` |
| Stage 6 response (this file) | `docs/sdlc/06-code-review-response.md` |
| Validator / routes patches | `flight_search/validator.py`, `flight_search/routes.py` |
| Flask pin | `requirements.txt` (`Flask==3.1.3`) |
| Tests | `tests/unit/test_validator.py`, `tests/integration/test_http.py` |

## Key Decisions

- Treat unhandled `ValueError` on passenger parse as **critical** (FR-8 / graceful invalid input).
- Enforce `YYYY-MM-DD` with a regex before `date.fromisoformat` (Python 3.11+ is looser than the FR).
- Bump Flask to 3.1.3 for CVE-2026-27205 (low; caching-proxy scenario).
- Leave remaining warnings (date `min` vs Playwright, duplicate `result-*` ids, CSRF TTL) for Stage 7 / later; they do not block Verify.
- Do not start Stage 7 until a human accepts this review.

## Open Questions / Blockers

- **Human approval of Stage 6** is required before Stage 7 Verify.
- Local workspace has **no git/gh on PATH**; the Stage 6 PR is opened via GitHub REST (`api-conf.properties` — not committed).
- No remaining product blockers. Do not commit `api-conf.properties`.

## PR

- **URL:** https://github.com/rkumar802212/CursorSdlc/pull/6
- **Title:** `[SDLC Stage 6] Code Review — KAN-1 Flask search`
- **Branch:** `sdlc/stage-6-code-review-kan-1` → `main`

## Ready for Human Approval

**Yes.** Please confirm the review, patches, and pytest results. Reply **approved** / **proceed to verify** (or request changes). Do **not** start Stage 7 until then.

---

# Code Review

## Summary

Peer review of the **KAN-1 Search flight** Flask app against `requirements.md`, `architecture.md`, `design-review.md`, and `impl-plan.md` (D1–D10). The implementation is a Python Flask + Jinja2 + in-memory JSON catalog with CSRF, fail-fast boot, seeded fixtures, and pytest coverage of the DOM/HTTP contract.

Review was not a rubber stamp. One **critical** defect was found and **fixed in this stage**: invalid passenger input that is `str.isdigit()` but not accepted by `int()` (for example Unicode superscript `¹`) raised `ValueError` in `validate_search` and became an HTTP 500 instead of a 200 validation message. Additional patches: ISO `YYYY-MM-DD` enforcement, Flask bump **3.0.3 → 3.1.3** (CVE-2026-27205), CSRF logs without stack traces, defensive `None` handling on POST search, and tighter tests.

**pytest after fixes: 34 passed.** Playwright MCP E2E remains **Stage 7** (placeholders only).

## Critical (must fix)

**None remaining.** Items found and patched in Stage 6:

1. **Invalid passengers could 500 instead of validating (FR-8 / NFR-4)**  
   - **Where (before):** `flight_search/validator.py` used `str.isdigit()` then `int(...)`. `routes.py` called `validate_search` **outside** the search `try/except`.  
   - **Why:** `isdigit()` is true for some non-ASCII digits; `int("¹")` raises `ValueError`. User-visible result was the generic 500 page, not a passenger validation error.  
   - **Fix applied:** Require ASCII digits, `int(..., 10)`, shared `PAX_ERROR`; unit test for `¹`. Remaining critical count: **0**.

## Warnings (should fix)

1. **HTML `min="{{ server_today }}"` on the date input** (`flight_search/templates/search.html` ~line 50)  
   Stage 7 past-date cases may need to set the value via the driver if the browser blocks dates below `min`. Use `data-testid="server-today"`.

2. **Duplicate `result-*` `data-testid`s when two cards render** (`search.html` 86–94)  
   Stage 7 **must** query `result-*` **inside** each `flight-card`.

3. **CSRF tokens never expire** (`flight_search/__init__.py`: `WTF_CSRF_TIME_LIMIT = None`)  
   Acceptable for local MVP.

4. **Catalog load checks keys only, not value types/non-empty** (`flight_search/repository.py` 65–73).

5. **Sort key is string `departure_time`** (`repository.py` 98–103) — keep catalog times zero-padded `HH:MM`.

6. **No `Cache-Control: private` on HTML** — optional if hosted behind a CDN later.

7. **Use committed run path only** (`python -m flight_search`, `debug=False`) for E2E.

## Suggestions (consider)

- Pin transitive dependencies with a lockfile.  
- Read `server-today` in the integration past-date test (same as E2E).  
- Stage 7: wait on `GET /health`, copy CSRF from GET `/`, never hardcode tokens.

## Checklist Results

| Area | Pass/Fail | Notes |
|------|-----------|-------|
| Correctness | **Pass** | FR-1–11 and D1–D9 match after patches; ISO date strictly `YYYY-MM-DD`. |
| Security | **Pass** | No secrets in app/docs; gitignore for `api-conf.properties` / `.env`; CSRF; autoescape; env `SECRET_KEY`; `debug=False`. |
| Error Handling | **Pass** | Fail-fast catalog; generic 400/404/500; passenger/date junk no longer 500s. |
| Test Coverage | **Pass** | Happy path, zero matches, missing/invalid fields, CSRF, trim, fail-fast JSON. Playwright is Stage 7. |
| Code Clarity | **Pass** | Names map to architecture. |
| DRY Principle | **Pass** | Shared normalize/today/safe_log. |
| Dependency Safety | **Pass** | Flask 3.1.3. Other pins appropriate. |
| Stack fit | **Pass** | Python Flask web app; no stack switch. |

## Recommended Fixes (ordered)

1. ~~Passenger `isdigit`/`int` 500~~ **Done**.  
2. ~~Strict ISO date + Flask 3.1.3 + CSRF log + tests~~ **Done**.  
3. Stage 7 Playwright: scope `result-*` inside `flight-card`; past date via `server-today`; CSRF from GET `/`.  
4. Optionally validate catalog value types at load; pin transitive deps.

## Ready for Verify Stage? (yes/no)

**yes** — no remaining critical defects. Human acceptance of Stage 6 is still required before Stage 7. Stage 7 must add **Playwright MCP** E2E scripts for happy path, validation, and no-results.
