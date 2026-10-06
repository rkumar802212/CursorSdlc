# Playwright E2E (Stage 7)

Durable pytest-playwright scripts against a live Flask process (`debug=False`).
Playwright MCP was unavailable in this workspace (live tool discovery failed);
scripts were authored from the frozen `data-testid` contract and executed with
the Playwright Python runner.

## Scripts

- `tests/e2e/test_search_happy.py`
- `tests/e2e/test_search_validation.py`
- `tests/e2e/test_search_no_results.py`
- `tests/e2e/helpers.py` — locators, CSRF, `server-today` date math, inner-card `result-*` queries
- `tests/e2e/conftest.py` — starts `python -m flight_search` unless `E2E_BASE_URL` already serves `/health`

Default `pytest` (unit/integration) does **not** collect this folder. Use:

```powershell
pip install -r requirements-e2e.txt
python -m playwright install chromium
pytest -c pytest-e2e.ini
```

Optional: start the app yourself, wait for `GET http://127.0.0.1:5000/health` → `{"status":"ok"}`, then set `E2E_BASE_URL=http://127.0.0.1:5000`.

## CSRF and dates

- CSRF comes from the hidden `csrf_token` on `GET /`. Never hardcode a token.
- Past-date cases use **yesterday relative to `data-testid="server-today"`**, not the browser clock.
- HTML `min` may block typing a past date; tests set the value via the driver (`set_date_value`).
- Happy path: `delhi` / `Mumbai` / `2099-06-15`.
- Zero matches: `Delhi` / `Kolkata` / `2099-12-31`.
- Duplicate `result-*` ids: queries are scoped **inside each** `flight-card`.

## DOM matrix

| Outcome | validation-errors | results-list / flight-card | no-flights | passenger-context |
|---------|-------------------|----------------------------|------------|-------------------|
| GET `/` | Hidden/empty | Not in DOM | Not in DOM | Not in DOM |
| Validation failure | Visible | Not in DOM | Not in DOM | Not in DOM |
| Valid, ≥1 match | Hidden/empty | Present | Not in DOM | Present |
| Valid, zero matches | Hidden/empty | Not in DOM | Visible | Present |
