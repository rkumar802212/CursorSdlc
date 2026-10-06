"""Stage 7 Playwright MCP placeholder — validation.

Do not execute this module in Stage 5.

Cases (all POST /search with CSRF from GET /):
- Same city: Delhi / delhi — validation-errors visible; results-list and
  no-flights not in DOM; passenger-context not in DOM
- Yesterday: derive from data-testid=server-today minus one day (server local)
- Missing required fields
- Passengers outside 1–9 (0, 10, 2.5)

Start Flask with debug=False; wait until GET /health returns {"status":"ok"}.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Stage 7 Playwright MCP — not executed in Stage 5"
)


def test_search_validation_placeholder():
    assert False, "Implemented and run in Stage 7"
