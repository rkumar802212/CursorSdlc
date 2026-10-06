"""Playwright E2E — validation errors (same city, past date, missing, pax)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.e2e.helpers import (
    assert_validation_visible,
    fill_search,
    open_home,
    submit_search,
    yesterday_iso,
)

import pytest

pytestmark = pytest.mark.e2e


def test_same_city_shows_validation(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    fill_search(
        page,
        departure="Delhi",
        arrival="delhi",
        travel_date="2099-06-15",
        passengers="1",
    )
    submit_search(page)
    assert_validation_visible(page)
    expect(page.locator('[data-testid="validation-errors"]')).to_contain_text(
        "different", ignore_case=True
    )


def test_past_date_from_server_today(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    past = yesterday_iso(page)
    fill_search(
        page,
        departure="Delhi",
        arrival="Mumbai",
        travel_date=past,
        passengers="1",
        bypass_date_min=True,
    )
    submit_search(page)
    assert_validation_visible(page)
    expect(page.locator('[data-testid="validation-errors"]')).to_contain_text(
        "past", ignore_case=True
    )


def test_missing_required_fields(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    fill_search(
        page,
        departure="",
        arrival="",
        travel_date="",
        passengers="",
    )
    submit_search(page)
    assert_validation_visible(page)


def test_passengers_outside_range(page: Page, e2e_base_url: str):
    open_home(page, e2e_base_url)
    for pax in ("0", "10", "2.5"):
        fill_search(
            page,
            departure="Delhi",
            arrival="Mumbai",
            travel_date="2099-06-15",
            passengers=pax,
        )
        submit_search(page)
        assert_validation_visible(page)
        open_home(page, e2e_base_url)
