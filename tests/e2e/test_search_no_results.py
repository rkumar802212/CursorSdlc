"""Stage 7 Playwright MCP placeholder — zero matches.

Do not execute this module in Stage 5.

Submit Delhi + Kolkata + 2099-12-31 (valid search; no catalog row).
Assert no-flights visible, results-list not in DOM, passenger-context present,
validation-errors hidden/empty.

Start: python -m flight_search (SECRET_KEY set, debug=False).
Wait: GET /health == {"status":"ok"} after catalog load.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Stage 7 Playwright MCP — not executed in Stage 5"
)


def test_search_no_results_placeholder():
    assert False, "Implemented and run in Stage 7"
