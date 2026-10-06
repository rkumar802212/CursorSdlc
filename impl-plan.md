# Implementation Plan

## Approach Summary

KAN-1 (Search flight) is implemented in **Stage 5** as a **Python Flask** web application with Jinja2 server-rendered HTML, Flask-WTF CSRF, and an in-memory dummy catalog loaded from JSON at process start. No FastAPI/Django switch (D1). No production application code is written in Stage 4.

**Runtime shape (from approved `architecture.md` + D1–D10):**

- Anonymous GET `/` renders the search form (CSRF token + `server-today`).
- POST `/search` validates, then filters the in-memory catalog; business validation stays HTTP 200 with HTML (errors, results, or empty state).
- GET `/search` returns **302 to `/`** (D5). Search is POST-only.
- GET `/health` returns `{"status":"ok"}` only after a successful catalog load (D8). Fail-fast: do not bind HTTP if `data/flights.json` is missing or malformed.
- Flask `debug=False` on committed run paths. `SECRET_KEY` from environment only (`.env.example` placeholder; never commit `.env` or `api-conf.properties`).

**Verify path (Stage 7, not executed now):** **Playwright MCP** E2E scripts drive the live Flask UI using frozen `data-testid` contracts (form ids + namespaced `result-*`, DOM state matrix). Unit/integration tests (pytest + Flask test client) cover validator, repository, CSRF, redirects, and health before E2E. Playwright copies the CSRF token from GET `/`, uses `server-today` for yesterday, and uses seeded dates `2099-06-15` (happy) and `2099-12-31` (no results).

**Stage 5 implements the app and unit/integration tests plus E2E folder prep. Stage 7 authors and runs Playwright MCP scripts. Stage 4 only plans.**

## Task List (dependency order)

| ID | Task | Depends On | Priority | Status | Notes |
|----|------|------------|----------|--------|-------|
| T01 | Flask project scaffold: `requirements.txt` / lock-friendly pins (Flask, Flask-WTF, pytest, python-dotenv as needed), app factory package, `SECRET_KEY` via env, `.env.example` local placeholder, confirm `.gitignore` covers `.env`, `api-conf.properties`, venv, pytest/Playwright output; committed run entry with **`debug=False`** | — | P0 | Done | Flask 3 + Flask-WTF + pytest. App factory; SECRET_KEY from env; `.env.example`; `debug=False` in `python -m flight_search` / `wsgi.py`. |
| T02 | Shared `normalize_city` (`strip` + `casefold`) and server-local `today` helper | T01 | P0 | Done | D3. Used by validator and repository. Whitespace-only cities are missing (not searched). |
| T03 | Dummy catalog `data/flights.json` with **seeded fixtures** (D6): ≥1 `Delhi`→`Mumbai` on `2099-06-15` (mixed-case cities, all display fields); **no** `Delhi`/`Kolkata`/`2099-12-31` row; optional second same-route flight for list coverage; fields: airline, flight_number, departure_city, arrival_city, travel_date, departure_time, arrival_time, duration, stops, price | T01 | P0 | Done | Two Delhi→Mumbai rows on 2099-06-15 (mixed case) plus Bengaluru→Chennai; no Kolkata 2099-12-31 row. |
| T04 | Flight repository: load JSON at startup **fail-fast** (missing/malformed → do not bind HTTP, safe log, do not invent flights); `search(...)` case-insensitive exact city + exact date; never mutate catalog; sort `departure_time` ASC then `flight_number` ASC; passengers never filter or change price (D9) | T02, T03 | P0 | Done | `FlightRepository.load` raises `CatalogLoadError`; search copies rows; passengers ignored. |
| T05 | Search validator: trim required fields; passengers integer 1–9 (reject `2.5`, letters, empty); ISO `YYYY-MM-DD`; today allowed, `date < today` rejected; same-city after `normalize_city` rejected; validation order per Data Flow | T02 | P0 | Done | FR-6–8. No repository call on failure. |
| T06 | Flask-WTF `SearchForm` + CSRF on POST `/search`; token from GET `/` only (never hardcoded); missing/invalid CSRF → generic **400**, no stack trace (D4) | T01, T05 | P0 | Done | CSRFProtect + CSRFError handler → generic 400 HTML. |
| T07 | Jinja2 templates (autoescape on): labels, HTML date input, optional `min` = `server-today` (UX only), **Search Flights**, all form `data-testid`s, namespaced `result-*` ids (D2), `server-today` (D7), `passenger-context` on valid search, copy equivalent to “No flights found”; **DOM state matrix** (initial / validation / matches / zero matches) | T01 | P0 | Done | `search.html` implements the frozen DOM matrix. User cities not marked `\|safe`. |
| T08 | HTTP routes: GET `/` empty form; POST `/search` 200 HTML (errors, results, or empty); GET `/search` **302 → `/`** (D5); GET `/health` JSON after successful load (D8) | T04, T06, T07 | P0 | Done | FR-1–11 surface. |
| T09 | Safe logger + 404/500 handlers: unexpected exceptions logged without secrets/request-body dumps; generic user HTML; no `api-conf.properties` contents | T01 | P1 | Done | `flight_search.safe_log`; generic 400/404/500 templates. |
| T10 | Fail-fast boot wiring: catalog load before `app.run` / WSGI serve; `/health` unreachable if process did not start | T04, T08 | P0 | Done | `create_app` loads catalog before routes; failed load raises and does not return an app. |
| T11 | Unit tests (pytest, no browser): `normalize_city`; passenger parse; same-city; past vs today; whitespace-as-missing; repository filter, sort, and no passenger price/inventory side effects; fail-fast load on bad/missing JSON | T02, T04, T05 | P0 | Done | `tests/unit/` — included in local pytest run. |
| T12 | Integration tests (Flask test client): GET `/` has CSRF + `server-today` + matrix initial state; POST valid happy path `delhi`/`Mumbai`/`2099-06-15`; zero match `Delhi`/`Kolkata`/`2099-12-31`; validation failures (same city, past date, missing, pax out of range) show `validation-errors` and **no** `results-list`/`no-flights`; GET `/search` 302; missing CSRF 400; `/health` 200 `ok`; passengers display-only | T08, T10, T11 | P0 | Done | `tests/integration/test_http.py` — 30 pytest tests passed locally. |
| T13 | Playwright E2E **prep** (not Stage 7 execution): reserve `tests/e2e/test_search_happy.py`, `test_search_validation.py`, `test_search_no_results.py`; document locators, CSRF copy-from-GET, `server-today` yesterday math, seeded dates; how to start Flask `debug=False` and wait on `/health` | T08, T12 | P1 | Done | Placeholders + `tests/e2e/README.md`. Not collected by pytest.ini. Full Playwright MCP is Stage 7. |
| T14 | App README / run notes: venv, env vars, `flights.json` path, local start, pytest, pointer to Stage 7 Playwright; no secrets | T01 | P2 | Done | Root `README.md`. |

## Critical Path

**T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08 → T10 → T11 → T12 → T13**

- T03 may run in parallel with T02 after T01 (catalog file vs helpers).
- T07 may run in parallel with T04–T06 after T01 (static template contracts are frozen).
- T09 may run in parallel after T01 and merge at T08.
- T14 is off the critical path except for operator docs.

This path delivers a running Flask search page, fail-fast catalog, CSRF, seeded fixtures, pytest, and E2E prep so Stage 7 Playwright MCP can execute without inventing contracts.

## Blocked Tasks

**Now (Stage 5 complete):** T01–T14 are implemented. Remaining gate is **human approval of Stage 5** before Stage 6 Code Review. Do not start Stage 6 until the human replies approved.

**Inside Stage 5 (dependency blocks — resolved):**

| Task | Blocked until |
|------|----------------|
| T02, T03, T07, T09, T14 | T01 scaffold exists |
| T04 | T02 + T03 |
| T05 | T02 |
| T06 | T01 + T05 |
| T08 | T04 + T06 + T07 |
| T10 | T04 + T08 |
| T11 | T02 + T04 + T05 |
| T12 | T08 + T10 + T11 |
| T13 | T08 + T12 (DOM/HTTP stable) |

**Not blocked by product questions:** D1–D10 and Stage 3 approval closed architecture locks. Residual MVP risks (single process, POST refresh, no rate limit) are accepted, not blockers.

**Stage 7 Playwright MCP execution** is blocked until Stage 5 implementation + Stage 6 code review are complete (pipeline order). T13 only prepares paths and contracts.

## Test Strategy Preview

### Unit / integration (Stage 5, pytest)

- **Validator:** required/whitespace; passengers 1–9 vs non-integer; ISO date; today allowed / yesterday rejected using injectable “today”; same-city after normalize (`Delhi` vs `delhi`).
- **Repository:** match `delhi`/`Mumbai`/`2099-06-15`; zero rows for `Delhi`/`Kolkata`/`2099-12-31`; sort order; ignore passengers; fail-fast on missing/invalid JSON.
- **Flask client:** CSRF present on GET `/`; POST with token; 400 without token; GET `/search` 302; `/health`; DOM-equivalent flags (presence of `validation-errors`, `results-list`, `no-flights`, `passenger-context`) matching the architecture matrix.

### Playwright MCP E2E (Stage 7 — plan only here)

Reserved scripts:

- `tests/e2e/test_search_happy.py` — open `/` unauthenticated; read CSRF + `server-today`; POST `delhi` / `Mumbai` / `2099-06-15` / pax 1–9; assert `flight-card` + `result-*` fields; `no-flights` not in DOM.
- `tests/e2e/test_search_validation.py` — same city; yesterday from **`server-today`** (not browser clock); missing fields; passengers outside 1–9; assert `validation-errors` visible; results and `no-flights` not in DOM.
- `tests/e2e/test_search_no_results.py` — `Delhi` + `Kolkata` + `2099-12-31`; `no-flights` visible; `results-list` not in DOM; `passenger-context` present.

E2E waits on `GET /health` after Flask start (`debug=False`). CSRF token is always taken from GET `/` (D4). Full Playwright MCP authoring and run is **Verify (Stage 7)**, not this stage.

## Definition of Done (per task / overall)

**Per task:** Implemented only in Stage 5+; for planning, a task is done when its Notes/acceptance mapping is satisfied, tests listed for that slice pass, and no secrets are introduced.

**Overall Stage 5 DoD (preview):**

- Flask app meets FR-1–11 and AC in `requirements.md`.
- D1–D9 behavior locked in code: Flask+JSON, `result-*` ids, `normalize_city`, CSRF, GET `/search` 302, D6 fixtures, `server-today`, fail-fast + `/health`, display-only passengers, `debug=False`.
- Unit + integration tests pass locally.
- Playwright scripts reserved/documented (T13); Stage 7 still required for Go/No-Go.
- `.gitignore` prevents `api-conf.properties` / `.env`; `.env.example` has no real secrets.

**Stage 4 DoD (this stage):** `impl-plan.md` complete with required sections; `docs/sdlc/04-impl-plan-response.md` written; Stage 4 GitHub PR opened; **no application source** added; human approval requested before coding.
