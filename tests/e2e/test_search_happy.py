"""Stage 7 Playwright MCP placeholder — happy path.

Do not execute this module in Stage 5. Stage 7 authors and runs Playwright MCP
against a live Flask server (`debug=False`) after GET /health is ok.

Locator contract (data-testid):
- Form: search-form, departure-city, arrival-city, travel-date, passengers,
  search-submit
- CSRF: copy hidden csrf_token from GET / (never hardcode)
- Today: read server-today (ISO YYYY-MM-DD); do not use the browser clock
- Seeded happy date: 2099-06-15; type delhi / Mumbai; passengers 1–9
- Assert: flight-card + result-* fields present; no-flights not in DOM;
  passenger-context present; validation-errors hidden/empty
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Stage 7 Playwright MCP — not executed in Stage 5"
)


def test_search_happy_placeholder():
    assert False, "Implemented and run in Stage 7"
