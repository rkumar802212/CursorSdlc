"""Playwright E2E — valid search with zero catalog matches."""

from __future__ import annotations

from playwright.sync_api import Page

from tests.e2e.helpers import assert_no_flights, fill_search, open_home, submit_search

import pytest

pytestmark = pytest.mark.e2e


def test_search_delhi_kolkata_no_flights(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    fill_search(
        page,
        departure="Delhi",
        arrival="Kolkata",
        travel_date="2099-12-31",
        passengers="1",
    )
    submit_search(page)
    assert_no_flights(page, passengers="1")
