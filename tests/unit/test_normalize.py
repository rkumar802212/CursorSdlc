from flight_search.normalize import normalize_city


def test_normalize_city_strips_and_casefolds():
    assert normalize_city("  Delhi ") == "delhi"
    assert normalize_city("MUMBAI") == "mumbai"
    assert normalize_city("delhi") == normalize_city("Delhi")


def test_normalize_city_none_and_whitespace():
    assert normalize_city(None) == ""
    assert normalize_city("   ") == ""
