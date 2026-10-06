"""Server-local calendar date helpers (D7)."""

from __future__ import annotations

from datetime import date
from collections.abc import Callable


def get_today(clock: Callable[[], date] | None = None) -> date:
    """Return process-local today. Tests may inject `clock`."""
    if clock is not None:
        return clock()
    return date.today()


def today_iso(clock: Callable[[], date] | None = None) -> str:
    return get_today(clock).isoformat()
