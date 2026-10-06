import json
from pathlib import Path

import pytest

from flight_search.repository import CatalogLoadError, FlightRepository

SEEDED_PATH = Path(__file__).resolve().parents[2] / "data" / "flights.json"


def test_seeded_happy_path_mixed_case():
    repo = FlightRepository.load(SEEDED_PATH)
    results = repo.search("delhi", "Mumbai", "2099-06-15", passengers=9)
    assert len(results) >= 1
    numbers = [row["flight_number"] for row in results]
    assert numbers == sorted(
        numbers,
        key=lambda n: (
            next(r["departure_time"] for r in results if r["flight_number"] == n),
            n,
        ),
    )
    times = [row["departure_time"] for row in results]
    assert times == sorted(times)


def test_sort_departure_time_then_flight_number():
    repo = FlightRepository.load(SEEDED_PATH)
    results = repo.search("Delhi", "Mumbai", "2099-06-15")
    pairs = [(r["departure_time"], r["flight_number"]) for r in results]
    assert pairs == sorted(pairs)


def test_zero_match_kolkata_fixture_absent():
    repo = FlightRepository.load(SEEDED_PATH)
    results = repo.search("Delhi", "Kolkata", "2099-12-31")
    assert results == []
    for row in repo._flights:
        assert not (
            str(row["travel_date"]) == "2099-12-31"
            and "kolkata" in str(row["arrival_city"]).casefold()
        )


def test_passengers_do_not_change_results_or_price():
    repo = FlightRepository.load(SEEDED_PATH)
    one = repo.search("Delhi", "Mumbai", "2099-06-15", passengers=1)
    nine = repo.search("Delhi", "Mumbai", "2099-06-15", passengers=9)
    assert [r["flight_number"] for r in one] == [r["flight_number"] for r in nine]
    assert [r["price"] for r in one] == [r["price"] for r in nine]


def test_search_does_not_mutate_catalog():
    repo = FlightRepository.load(SEEDED_PATH)
    before = [dict(r) for r in repo._flights]
    results = repo.search("delhi", "mumbai", "2099-06-15")
    results[0]["price"] = "mutated"
    after = [dict(r) for r in repo._flights]
    assert before == after


def test_fail_fast_missing_json(tmp_path: Path):
    missing = tmp_path / "nope.json"
    with pytest.raises(CatalogLoadError):
        FlightRepository.load(missing)


def test_fail_fast_malformed_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        FlightRepository.load(bad)


def test_fail_fast_empty_list(tmp_path: Path):
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        FlightRepository.load(empty)


def test_fail_fast_missing_fields(tmp_path: Path):
    incomplete = tmp_path / "inc.json"
    incomplete.write_text(json.dumps([{"airline": "X"}]), encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        FlightRepository.load(incomplete)
