# Code Review

## Summary

Peer review of the **KAN-1 Search flight** Flask app against `requirements.md`, `architecture.md`, `design-review.md`, and `impl-plan.md` (D1–D10). The implementation is a Python Flask + Jinja2 + in-memory JSON catalog with CSRF, fail-fast boot, seeded fixtures, and pytest coverage of the DOM/HTTP contract.

Review was not a rubber stamp. One **critical** defect was found and **fixed in this stage**: invalid passenger input that is `str.isdigit()` but not accepted by `int()` (for example Unicode superscript `¹`) raised `ValueError` in `validate_search` and became an HTTP 500 instead of a 200 validation message. Additional patches: ISO `YYYY-MM-DD` enforcement (Python 3.11+ `date.fromisoformat` is looser than the spec), Flask bump **3.0.3 → 3.1.3** (CVE-2026-27205), CSRF logs without stack traces, defensive `None` handling on POST search, and tighter tests.

**pytest after fixes: 34 passed.** Playwright MCP E2E remains **Stage 7** (placeholders only).

## Critical (must fix)

**None remaining.** Items found and patched in Stage 6:

1. **Invalid passengers could 500 instead of validating (FR-8 / NFR-4)**  
   - **Where (before):** `flight_search/validator.py` used `str.isdigit()` then `int(...)`. `routes.py` called `validate_search` **outside** the search `try/except`.  
   - **Why:** `isdigit()` is true for some non-ASCII digits; `int("¹")` raises `ValueError`. User-visible result was the generic 500 page, not a passenger validation error, and no search should run.  
   - **Fix applied:** Require ASCII digits, `int(..., 10)`, shared `PAX_ERROR`; unit test for `¹`. Remaining critical count: **0**.

## Warnings (should fix)

1. **HTML `min="{{ server_today }}"` on the date input** (`flight_search/templates/search.html` ~line 50)  
   Server validation remains source of truth (today allowed, yesterday rejected). Stage 7 Playwright past-date cases may need to set the value via the driver if the browser blocks typing a date below `min`. Derive yesterday from `data-testid="server-today"`, not the browser clock.

2. **Duplicate `result-*` `data-testid`s when two cards render** (`search.html` 86–94; happy path has two Delhi→Mumbai rows)  
   Architecture requires namespaced ids, not unique-per-row ids. Stage 7 **must** query `result-*` **inside** each `flight-card` (Playwright strict mode fails on page-level `getByTestId`).

3. **CSRF tokens never expire** (`flight_search/__init__.py`: `WTF_CSRF_TIME_LIMIT = None`)  
   Acceptable for local MVP; consider a finite limit if this process is ever exposed beyond localhost.

4. **Catalog load checks keys only, not value types/non-empty** (`flight_search/repository.py` 65–73)  
   Malformed-but-keyed rows (empty city, non-ISO date) can load. Seeded `data/flights.json` is valid. Optional: reject empty strings / non-ISO `travel_date` at load.

5. **Sort key is string `departure_time`** (`repository.py` 98–103)  
   Zero-padded `HH:MM` in the seed file sorts correctly. Unpadded times (e.g. `9:00` vs `14:40`) would mis-order. Keep catalog times `HH:MM`.

6. **No `Cache-Control: private` on HTML**  
   CVE-2026-27205 is low and needs a caching proxy. Flask is now **3.1.3**. Still worth `Cache-Control: private` if hosted behind a CDN later (out of MVP scope).

7. **Committed run path is `python -m flight_search` / `wsgi.py` with `debug=False`**  
   `flask run` with `FLASK_DEBUG=1` is not a committed path; operators should not use it for E2E.

## Suggestions (consider)

- Add a pip lock (`pip freeze` or `uv.lock`) so Werkzeug/Jinja transitive versions stay reproducible.  
- Integration past-date test could read `server-today` from HTML (same as E2E) instead of `date.today()`.  
- Optional `Cache-Control: no-store` on POST `/search`.  
- Do not mark user cities `|safe` (already followed).  
- Stage 7: wait on `GET /health`, copy CSRF from GET `/`, never hardcode tokens.

## Checklist Results

| Area | Pass/Fail | Notes |
|------|-----------|-------|
| Correctness | **Pass** | FR-1–11 and D1–D9 match: anonymous GET `/`, POST `/search`, case-insensitive exact city+date, same-city/past/pax/missing validation without results, seeded happy + no-results, display-only passengers, `result-*` fields. ISO date now strictly `YYYY-MM-DD`. |
| Security | **Pass** | No secrets in app/docs; `.gitignore` covers `api-conf.properties` and `.env`; Jinja autoescape; CSRFProtect + generic 400; `SECRET_KEY` from env; `debug=False`; user input not `|safe`. Do **not** commit `api-conf.properties`. |
| Error Handling | **Pass** | Fail-fast catalog; generic 400/404/500 HTML; CSRF type-only log; passenger/date parse no longer 500s on junk input; empty catalog refused. |
| Test Coverage | **Pass** | Happy path, zero matches, missing fields, pax range/non-integer, same city, past date, CSRF missing/invalid, trim match, fail-fast JSON, health, GET `/search` 302. Playwright E2E **not** in this stage (NFR-2 → Stage 7). |
| Code Clarity | **Pass** | Names map to architecture (`normalize_city`, `FlightRepository.load`, `validate_search`, `create_app`). |
| DRY Principle | **Pass** | Shared normalize/today/safe_log; form vs validator split is intentional (D4 vs FR-6–8). |
| Dependency Safety | **Pass** | Flask **3.1.3** (fixes CVE-2026-27205 on 3.0.3). Flask-WTF 1.2.1 / WTForms 3.1.2 / pytest 8.3.3 / python-dotenv 1.0.1 are appropriate. Transitive pins still optional. |
| Stack fit | **Pass** | Python Flask web app per `architecture.md` / `impl-plan.md`. No FastAPI/Django switch. |

## Recommended Fixes (ordered)

1. ~~Passenger `isdigit`/`int` 500~~ **Done** (`validator.py`, tests).  
2. ~~Strict ISO date + Flask 3.1.3 + CSRF log + test tautology~~ **Done**.  
3. Stage 7 Playwright: scope `result-*` inside `flight-card`; past date via `server-today`; CSRF from GET `/`.  
4. Optionally validate catalog value types at load; pin transitive deps.

## Ready for Verify Stage? (yes/no)

**yes** — no remaining critical defects. Human should accept this Stage 6 review (and the patches) before Stage 7 Verify. Stage 7 must author and run **Playwright MCP** E2E scripts (`tests/e2e/test_search_happy.py`, `test_search_validation.py`, `test_search_no_results.py`) against Flask `debug=False` after `/health` is ok.

## Fixes applied in this review

| Change | Why |
|--------|-----|
| `flight_search/validator.py` | ASCII passenger digits; ISO date regex before `fromisoformat` |
| `flight_search/routes.py` | Safe `None` strip on search fields; CSRF log without traceback |
| `requirements.txt` | `Flask==3.1.3` |
| `tests/unit/test_validator.py` | Unicode pax; invalid/non-ISO dates |
| `tests/integration/test_http.py` | Hidden errors on happy path; invalid CSRF; trim match; `2.5` pax HTTP |

**pytest:** 34 passed, 0 failed.
