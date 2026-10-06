from datetime import date

from flight_search.dates import get_today, today_iso


def test_get_today_injectable_clock():
    assert get_today(clock=lambda: date(2099, 1, 2)) == date(2099, 1, 2)
    assert today_iso(clock=lambda: date(2099, 1, 2)) == "2099-01-02"
