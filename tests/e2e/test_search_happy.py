"""Playwright E2E — happy path (anonymous GET /, POST /search)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.e2e.helpers import (
    RESULT_FIELDS,
    assert_happy_results,
    csrf_input,
    fill_search,
    open_home,
    submit_search,
    tid,
)

import pytest

pytestmark = pytest.mark.e2e


def test_anonymous_home_shows_form_and_csrf(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    expect(csrf_input(page)).to_have_count(1)
    token = csrf_input(page).input_value()
    assert token, "CSRF token must be present on GET / (never hardcoded)"
    expect(tid(page, "departure-city")).to_be_visible()
    expect(tid(page, "arrival-city")).to_be_visible()
    expect(tid(page, "travel-date")).to_be_visible()
    expect(tid(page, "passengers")).to_be_visible()
    expect(tid(page, "search-submit")).to_have_text("Search Flights")
    expect(tid(page, "server-today")).to_be_visible()
    expect(tid(page, "validation-errors")).to_be_hidden()
    assert tid(page, "results-list").count() == 0
    assert tid(page, "no-flights").count() == 0
    assert tid(page, "passenger-context").count() == 0


def test_search_happy_delhi_mumbai_case_insensitive(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    fill_search(
        page,
        departure="delhi",
        arrival="Mumbai",
        travel_date="2099-06-15",
        passengers="2",
    )
    submit_search(page)
    assert_happy_results(page, passengers="2")
    cards = tid(page, "flight-card")
    for i in range(cards.count()):
        card = cards.nth(i)
        dep = card.locator('[data-testid="result-departure-city"]').inner_text()
        arr = card.locator('[data-testid="result-arrival-city"]').inner_text()
        assert dep.casefold() == "delhi"
        assert arr.casefold() == "mumbai"
        for field in RESULT_FIELDS:
            expect(card.locator(f'[data-testid="{field}"]')).to_be_visible()


def test_get_search_redirects_home(page: Page, e2e_base_url: str):
    raw = page.request.get(f"{e2e_base_url}/search", max_redirects=0)
    assert raw.status == 302
    location = raw.headers.get("location", "")
    assert location.endswith("/")
    page.goto(f"{e2e_base_url}/search", wait_until="domcontentloaded")
    assert page.url.rstrip("/") == e2e_base_url.rstrip("/")
    expect(tid(page, "search-form")).to_be_visible()
    assert tid(page, "results-list").count() == 0
