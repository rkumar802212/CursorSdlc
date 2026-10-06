# Design Review

## Summary

Stage 2 architecture for Jira **KAN-1 (Search flight)** is a sound MVP: a single Flask process, Jinja2 search UI, in-process validator, and in-memory JSON dummy catalog, with Playwright targeting GET `/` and POST `/search`. Flask is an appropriate fit versus FastAPI or Django. No live APIs, auth, or booking — aligned with `requirements.md` out of scope.

The review is **not** a rubber stamp. Completeness vs acceptance criteria is largely good (FR-1–11 and AC map to components), but the original Interfaces contract would have broken Stage 7: form and result cards reused the same `data-testid` names (`departure-city`, `arrival-city`). Validation vs repository city matching omitted consistent **trim**, CSRF and GET `/search` were underspecified, catalog fixtures were not frozen, and “today” for past-date tests could drift across timezones. Those gaps are closed in `architecture.md` (see Architecture Updates Made). Residual risks are MVP-scale (single process, POST refresh, no rate limits).

**Approval Status** is **pending human acceptance**. Do not start Stage 4 Implementation Planning until the human accepts this review.

## Findings

### Critical

1. **Colliding Playwright `data-testid` values (testability / NFR verification)**  
   - **Where:** `architecture.md` Interfaces / Contracts (original): form ids `departure-city` / `arrival-city` and result inner ids listed as the same names (“or text within `flight-card`”).  
   - **Why it matters:** Stage 7 Playwright (`requirements.md` NFR-2, AC Playwright) cannot uniquely target form vs card. Duplicate test ids make E2E non-deterministic.  
   - **Fix applied:** Namespaced result ids (`result-airline`, `result-departure-city`, …) and an explicit DOM state matrix (validation vs results vs `no-flights`).

### Warnings

1. **City matching vs trim (`requirements.md` Clarifications / FR-5–6 vs Data Flow)**  
   Original repository match used `casefold()` only; same-city validation mentioned trim but search did not. `"delhi "` would fail exact match and whitespace-only cities might search instead of validating.  
   **Fix applied:** Shared `normalize_city = strip + casefold`; whitespace-only treated as missing.

2. **CSRF left optional (`architecture.md` Open Trade-offs vs Security)**  
   Preferring Flask-WTF without requiring it would split Stage 5 and Playwright (token vs bare POST).  
   **Fix applied:** Flask-WTF **required**; Playwright copies token from GET `/`; missing CSRF → generic 400.

3. **GET `/search` unspecified**  
   Form POSTs to `/search`; browsers, bookmarks, or Playwright mistakes could GET that path (405 vs empty search vs accidental query).  
   **Fix applied:** GET `/search` **302 to `/`**.

4. **Catalog fixtures not frozen**  
   Architecture required “some” matching and zero-match data but no cities/dates. Stage 5 and 7 could invent incompatible seeds; happy-path dates near “today” become past.  
   **Fix applied:** Seed table — `Delhi`→`Mumbai` on `2099-06-15`; zero match `Delhi`+`Kolkata`+`2099-12-31`.

5. **Past-date “today” vs Playwright clock (`requirements.md` Clarifications item 6)**  
   Server/local today vs browser TZ would flake yesterday tests.  
   **Fix applied:** `data-testid="server-today"` on GET `/`; E2E must derive yesterday from that value.

6. **Fail-fast vs `/health` dual wording (`Failure Modes`)**  
   “Fails fast **or** health unhealthy” allowed a listening app with an empty catalog that looks like “No flights found” for every query (contradicts FR-10 semantics).  
   **Fix applied:** Do not bind HTTP until JSON loads; `/health` is required only after successful load.

7. **Flask debug / Werkzeug debugger (`Security & Secret Handling`, NFR-3–4)**  
   Default Flask debug can expose stack traces and a debugger PIN.  
   **Fix applied:** `debug=False` in committed run paths.

8. **Unstable result order (`Components`: “stable display order”)**  
   Unspecified sort makes Playwright nth-card assertions flake if JSON key order changes.  
   **Fix applied:** `departure_time` ASC, then `flight_number` ASC.

9. **`results-list` “absent or empty” ambiguity**  
   Invalid vs zero-match vs success were not distinguishable by contract.  
   **Fix applied:** DOM state matrix; zero matches must **not** include `results-list`.

### Suggestions

1. HTML `min` on the date input matching `server-today` (UX only; server validation remains source of truth).  
2. Visible validation copy can stay product-owned; architecture does not freeze exact English except empty state equivalent to “No flights found” (`requirements.md` FR-10).  
3. pytest should unit-test `normalize_city`, passenger parse, and repository filters without Flask (already implied in Technology Choices).  
4. Single-process SPOF is acceptable for this dummy MVP; no extra cache or replica.  
5. Rate limiting and production WSGI remain out of scope (local 2s NFR).  
6. Price remains display-as-JSON; no currency localization (already a trade-off).

## Decisions Agreed

These are **reviewer-proposed locks** for human acceptance (not a substitute for the approval gate):

| ID | Decision |
|----|----------|
| D1 | Keep **Flask + Jinja2 + in-memory JSON**; do not switch to FastAPI/Django for KAN-1. |
| D2 | Result `data-testid`s are namespaced `result-*`; form ids stay as originally listed. |
| D3 | Shared **trim + casefold** city normalize; whitespace-only fields are validation errors. |
| D4 | **Flask-WTF CSRF required**; Playwright always submits the GET `/` token. |
| D5 | GET `/search` redirects to GET `/`; search is POST-only. |
| D6 | Seeded fixtures: happy `Delhi`/`Mumbai`/`2099-06-15`; no-results `Delhi`/`Kolkata`/`2099-12-31`. |
| D7 | `server-today` is the only source of “today” for E2E past-date tests. |
| D8 | Catalog load **fail-fast**; `/health` required after successful boot. |
| D9 | Passengers remain display-only (FR-11); no inventory or price change. |
| D10 | No production code and no Implementation Planning until human accepts this review. |

## Architecture Updates Made

Updated `architecture.md` (required headings preserved):

- Interfaces: unique `result-*` test ids; DOM state matrix; `server-today`; GET `/search` 302; CSRF on POST; `/health` after load.
- Data Flow: `normalize_city`; trim/whitespace-as-missing; integer passengers; CSRF.
- Components: fail-fast catalog; sort order; seeded fixtures pointer.
- Technology: Flask-WTF required; `debug=False`.
- Failure Modes: CSRF 400; no silent empty catalog; zero-match DOM matches matrix.
- Open Trade-offs: CSRF required; namespaced test ids; health required.
- Seeded catalog fixture table for Stage 5/7.

## Residual Risks

- **Single Flask process / in-memory catalog:** process crash loses nothing durable but takes search offline (acceptable MVP SPOF).  
- **POST-render 200:** browser refresh re-POSTs (documented trade-off).  
- **CSRF + `SECRET_KEY`:** misconfigured env fails POST; must be in `.env.example` only, never committed secrets.  
- **Dummy prices/schedules** can look “real” to users; UX should not imply booking (out of scope).  
- **No rate limiting** on anonymous POST (local/dev only).  
- **JSON catalog is the test oracle:** if Stage 5 omits seeded rows, Verify fails — mitigated by the fixture table, not by runtime checks.

## Approval Status

**Pending human acceptance.**

Please confirm the findings, architecture updates, and Decisions Agreed (D1–D10). Reply **approved** / **accept design review** (or request changes) before Stage 4 Implementation Planning. Do not implement the Python web app until then.
