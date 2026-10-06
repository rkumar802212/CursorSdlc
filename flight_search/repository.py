"""In-memory dummy flight catalog loaded from JSON at process start (D8)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from flight_search.normalize import normalize_city
from flight_search.safe_log import log_event

REQUIRED_FIELDS = (
    "airline",
    "flight_number",
    "departure_city",
    "arrival_city",
    "travel_date",
    "departure_time",
    "arrival_time",
    "duration",
    "stops",
    "price",
)


class CatalogLoadError(Exception):
    """Raised when the dummy catalog cannot be loaded. Process must not bind HTTP."""


def _as_date_str(travel_date: date | str) -> str:
    if isinstance(travel_date, date):
        return travel_date.isoformat()
    return str(travel_date)


class FlightRepository:
    def __init__(self, flights: list[dict[str, Any]]):
        # Store copies so callers cannot mutate the catalog.
        self._flights: tuple[dict[str, Any], ...] = tuple(
            dict(row) for row in flights
        )

    @classmethod
    def load(cls, path: Path) -> FlightRepository:
        catalog_path = Path(path)
        if not catalog_path.is_file():
            log_event(f"Catalog missing at path={catalog_path}")
            raise CatalogLoadError(f"Catalog file not found: {catalog_path}")
        try:
            raw = catalog_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            log_event(f"Catalog JSON is malformed at path={catalog_path}")
            raise CatalogLoadError("Catalog JSON is malformed") from exc
        except OSError as exc:
            log_event(f"Catalog could not be read at path={catalog_path}")
            raise CatalogLoadError("Catalog could not be read") from exc

        if not isinstance(data, list) or len(data) == 0:
            log_event(f"Catalog empty or not a list at path={catalog_path}")
            raise CatalogLoadError("Catalog must be a non-empty JSON list")

        flights: list[dict[str, Any]] = []
        for index, row in enumerate(data):
            if not isinstance(row, dict):
                raise CatalogLoadError(f"Catalog row {index} is not an object")
            missing = [key for key in REQUIRED_FIELDS if key not in row]
            if missing:
                raise CatalogLoadError(
                    f"Catalog row {index} missing required fields"
                )
            flights.append(dict(row))

        log_event(f"Catalog loaded rows={len(flights)}")
        return cls(flights)

    def search(
        self,
        departure_city: str,
        arrival_city: str,
        travel_date: date | str,
        passengers: int | None = None,
    ) -> list[dict[str, Any]]:
        """Filter by normalized city + exact date. Passengers are ignored (D9)."""
        del passengers  # display-only; never filter or change price
        want_dep = normalize_city(departure_city)
        want_arr = normalize_city(arrival_city)
        want_date = _as_date_str(travel_date)
        matches: list[dict[str, Any]] = []
        for row in self._flights:
            if (
                normalize_city(row["departure_city"]) == want_dep
                and normalize_city(row["arrival_city"]) == want_arr
                and str(row["travel_date"]) == want_date
            ):
                matches.append(dict(row))
        matches.sort(
            key=lambda flight: (
                str(flight["departure_time"]),
                str(flight["flight_number"]),
            )
        )
        return matches
