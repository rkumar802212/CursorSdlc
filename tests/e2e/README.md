# Playwright E2E (Stage 7) — Stage 5 prep only

These scripts are **placeholders**. Do **not** run a full Playwright MCP suite
as part of Stage 5. Stage 7 (Verify) authors and executes the tests.

## Reserved files

- `tests/e2e/test_search_happy.py`
- `tests/e2e/test_search_validation.py`
- `tests/e2e/test_search_no_results.py`

`pytest.ini` does not collect this folder.

## Start the app for E2E

1. Create a venv and `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and set `SECRET_KEY` (local only).
3. Confirm `data/flights.json` exists (seeded Delhi→Mumbai on `2099-06-15`).
4. Run with **debug off**:

   `python -m flight_search`

5. Wait until `GET http://127.0.0.1:5000/health` returns `{"status":"ok"}`.
   Health is reachable only after a successful catalog load.

## CSRF and dates

- Open `GET /` unauthenticated.
- Copy the hidden `csrf_token` from the form. Never hardcode a token.
- Read `data-testid="server-today"` for the process-local ISO date.
- Past-date cases use **yesterday relative to `server-today`**, not the browser clock.
- Happy path: `delhi` / `Mumbai` / `2099-06-15`.
- Zero matches: `Delhi` / `Kolkata` / `2099-12-31`.

## DOM matrix

| Outcome | validation-errors | results-list / flight-card | no-flights | passenger-context |
|---------|-------------------|----------------------------|------------|-------------------|
| GET `/` | Hidden/empty | Not in DOM | Not in DOM | Not in DOM |
| Validation failure | Visible | Not in DOM | Not in DOM | Not in DOM |
| Valid, ≥1 match | Hidden/empty | Present | Not in DOM | Present |
| Valid, zero matches | Hidden/empty | Not in DOM | Visible | Present |

Result field ids are namespaced: `result-airline`, `result-flight-number`,
`result-departure-city`, `result-arrival-city`, `result-departure-time`,
`result-arrival-time`, `result-duration`, `result-stops`, `result-price`.
Do not reuse form test ids on cards.
