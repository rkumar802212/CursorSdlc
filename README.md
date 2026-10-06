# KAN-1 Search flight (Flask)

Python Flask web app for dummy flight search (Agentic SDLC Stage 5). No live airline APIs, booking, or authentication.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set `SECRET_KEY` in `.env` to a local-only value. Never commit `.env`, `api-conf.properties`, or tokens.

Catalog path: `data/flights.json` (loaded at process start). If the file is missing or malformed, the process **does not start** (no HTTP bind).

## Run locally

`debug` is always `False` on committed run paths.

```powershell
python -m flight_search
```

Equivalent WSGI object: `wsgi:app`.

- Search form: http://127.0.0.1:5000/
- Health (only after catalog load): http://127.0.0.1:5000/health → `{"status":"ok"}`

## Tests

Unit and Flask test-client integration:

```powershell
pytest
```

Playwright E2E (Stage 7) — does not run with default `pytest`:

```powershell
pip install -r requirements-e2e.txt
python -m playwright install chromium
pytest -c pytest-e2e.ini
```

See `tests/e2e/README.md`. Scripts start `python -m flight_search` (`debug=False`) unless `E2E_BASE_URL` already returns `{"status":"ok"}` on `/health`. CSRF is taken from `GET /`. Past dates use `data-testid="server-today"`. Seeded dates: `2099-06-15` (happy), `2099-12-31` (no results for Delhi→Kolkata).
