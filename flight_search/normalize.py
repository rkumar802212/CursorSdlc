"""Shared city normalization (D3)."""


def normalize_city(value: str) -> str:
    """Return a comparable city key: strip whitespace then casefold."""
    if value is None:
        return ""
    return str(value).strip().casefold()
