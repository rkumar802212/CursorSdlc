"""Search form validation (FR-6–8) in Data Flow order."""

from __future__ import annotations

from datetime import date

from flight_search.dates import get_today
from flight_search.normalize import normalize_city


def validate_search(
    departure_city: str | None,
    arrival_city: str | None,
    travel_date: str | None,
    passengers: str | None,
    *,
    today: date | None = None,
) -> list[str]:
    """Return user-visible error messages. Empty list means valid.

    Order: presence → passenger integer 1–9 → ISO date → not past → cities differ.
    """
    errors: list[str] = []
    today_date = today if today is not None else get_today()

    dep = "" if departure_city is None else str(departure_city)
    arr = "" if arrival_city is None else str(arrival_city)
    date_raw = "" if travel_date is None else str(travel_date)
    pax_raw = "" if passengers is None else str(passengers)

    if not dep.strip():
        errors.append("Departure city is required.")
    if not arr.strip():
        errors.append("Arrival city is required.")
    if not date_raw.strip():
        errors.append("Travel date is required.")
    if not pax_raw.strip():
        errors.append("Number of passengers is required.")

    pax_stripped = pax_raw.strip()
    if pax_stripped:
        if not pax_stripped.isdigit():
            errors.append("Passengers must be a whole number from 1 to 9.")
        else:
            pax_value = int(pax_stripped)
            if pax_value < 1 or pax_value > 9:
                errors.append("Passengers must be a whole number from 1 to 9.")

    parsed_date: date | None = None
    date_stripped = date_raw.strip()
    if date_stripped:
        try:
            parsed_date = date.fromisoformat(date_stripped)
        except ValueError:
            errors.append("Travel date must be YYYY-MM-DD.")
        else:
            if parsed_date < today_date:
                errors.append("Travel date cannot be in the past.")

    if dep.strip() and arr.strip():
        if normalize_city(dep) == normalize_city(arr):
            errors.append("Departure and arrival cities must be different.")

    return errors


def parse_passengers(passengers: str) -> int:
    return int(str(passengers).strip())
