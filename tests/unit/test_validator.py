from datetime import date

from flight_search.validator import validate_search


FIXED_TODAY = date(2026, 10, 6)


def test_whitespace_cities_are_missing():
    errors = validate_search("   ", "Mumbai", "2099-06-15", "1", today=FIXED_TODAY)
    assert any("Departure city is required" in e for e in errors)


def test_missing_required_fields():
    errors = validate_search("", "", "", "", today=FIXED_TODAY)
    assert any("Departure city" in e for e in errors)
    assert any("Arrival city" in e for e in errors)
    assert any("Travel date" in e for e in errors)
    assert any("passengers" in e.lower() for e in errors)


def test_passengers_reject_non_integer_and_range():
    assert any(
        "Passengers" in e
        for e in validate_search("Delhi", "Mumbai", "2099-06-15", "2.5", today=FIXED_TODAY)
    )
    assert any(
        "Passengers" in e
        for e in validate_search("Delhi", "Mumbai", "2099-06-15", "abc", today=FIXED_TODAY)
    )
    assert any(
        "Passengers" in e
        for e in validate_search("Delhi", "Mumbai", "2099-06-15", "0", today=FIXED_TODAY)
    )
    assert any(
        "Passengers" in e
        for e in validate_search("Delhi", "Mumbai", "2099-06-15", "10", today=FIXED_TODAY)
    )
    assert validate_search("Delhi", "Mumbai", "2099-06-15", "1", today=FIXED_TODAY) == []
    assert validate_search("Delhi", "Mumbai", "2099-06-15", "9", today=FIXED_TODAY) == []
    unicode_digit = validate_search(
        "Delhi", "Mumbai", "2099-06-15", "¹", today=FIXED_TODAY
    )
    assert any("Passengers" in e for e in unicode_digit)


def test_today_allowed_yesterday_rejected():
    today_ok = validate_search(
        "Delhi", "Mumbai", FIXED_TODAY.isoformat(), "1", today=FIXED_TODAY
    )
    assert today_ok == []
    yesterday = validate_search(
        "Delhi", "Mumbai", "2026-10-05", "1", today=FIXED_TODAY
    )
    assert any("past" in e.lower() for e in yesterday)


def test_same_city_after_normalize():
    errors = validate_search("Delhi", "delhi", "2099-06-15", "1", today=FIXED_TODAY)
    assert any("different" in e.lower() for e in errors)


def test_invalid_and_non_iso_dates():
    compact = validate_search(
        "Delhi", "Mumbai", "20990615", "1", today=FIXED_TODAY
    )
    assert any("YYYY-MM-DD" in e for e in compact)
    slashes = validate_search(
        "Delhi", "Mumbai", "2099/06/15", "1", today=FIXED_TODAY
    )
    assert any("YYYY-MM-DD" in e for e in slashes)
    impossible = validate_search(
        "Delhi", "Mumbai", "2099-02-31", "1", today=FIXED_TODAY
    )
    assert any("YYYY-MM-DD" in e for e in impossible)
