"""Playwright locators and DOM-matrix helpers for KAN-1 search."""

from __future__ import annotations

from datetime import date, timedelta

from playwright.sync_api import Page, expect

RESULT_FIELDS = (
    "result-airline",
    "result-flight-number",
    "result-departure-city",
    "result-arrival-city",
    "result-departure-time",
    "result-arrival-time",
    "result-duration",
    "result-stops",
    "result-price",
)


def tid(page: Page, name: str):
    return page.locator(f'[data-testid="{name}"]')


def open_home(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/", wait_until="domcontentloaded")
    expect(tid(page, "search-form")).to_be_visible()


def csrf_input(page: Page):
    return page.locator('input[name="csrf_token"]')


def server_today(page: Page) -> str:
    text = tid(page, "server-today").inner_text().strip()
    date.fromisoformat(text)
    return text


def yesterday_iso(page: Page) -> str:
    today = date.fromisoformat(server_today(page))
    return (today - timedelta(days=1)).isoformat()


def set_date_value(page: Page, iso_date: str) -> None:
    """Set travel-date even when HTML min blocks typing a past date."""
    tid(page, "travel-date").evaluate(
        """(el, value) => {
            el.removeAttribute('min');
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            if (el.form) {
                el.form.setAttribute('novalidate', '');
            }
        }""",
        iso_date,
    )


def fill_search(
    page: Page,
    *,
    departure: str,
    arrival: str,
    travel_date: str,
    passengers: str,
    bypass_date_min: bool = False,
) -> None:
    tid(page, "departure-city").fill(departure)
    tid(page, "arrival-city").fill(arrival)
    if bypass_date_min:
        set_date_value(page, travel_date)
    else:
        tid(page, "travel-date").fill(travel_date)
    tid(page, "passengers").fill(passengers)


def submit_search(page: Page) -> None:
    tid(page, "search-submit").click()
    page.wait_for_load_state("domcontentloaded")


def assert_validation_visible(page: Page) -> None:
    region = tid(page, "validation-errors")
    expect(region).to_be_visible()
    assert region.get_attribute("hidden") is None
    assert region.inner_text().strip() != ""
    assert tid(page, "results-list").count() == 0
    assert tid(page, "flight-card").count() == 0
    assert tid(page, "no-flights").count() == 0
    assert tid(page, "passenger-context").count() == 0


def assert_validation_hidden(page: Page) -> None:
    region = tid(page, "validation-errors")
    expect(region).to_have_count(1)
    expect(region).to_be_hidden()


def assert_happy_results(page: Page, *, passengers: str) -> None:
    assert_validation_hidden(page)
    expect(tid(page, "results-list")).to_be_visible()
    cards = tid(page, "flight-card")
    expect(cards).to_have_count(2)
    numbers = set()
    for i in range(cards.count()):
        card = cards.nth(i)
        for field in RESULT_FIELDS:
            inner = card.locator(f'[data-testid="{field}"]')
            expect(inner).to_have_count(1)
            assert inner.inner_text().strip() != ""
        numbers.add(card.locator('[data-testid="result-flight-number"]').inner_text().strip())
    assert numbers == {"6E-201", "AI-440"}
    expect(tid(page, "passenger-context")).to_contain_text(f"Passengers: {passengers}")
    assert tid(page, "no-flights").count() == 0


def assert_no_flights(page: Page, *, passengers: str) -> None:
    assert_validation_hidden(page)
    expect(tid(page, "no-flights")).to_be_visible()
    expect(tid(page, "no-flights")).to_have_text("No flights found")
    assert tid(page, "results-list").count() == 0
    assert tid(page, "flight-card").count() == 0
    expect(tid(page, "passenger-context")).to_contain_text(f"Passengers: {passengers}")
