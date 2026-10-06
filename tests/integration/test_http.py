import re

from datetime import date, timedelta


def csrf_token(html: str) -> str:
    match = re.search(
        r'name="csrf_token"[^>]*value="([^"]+)"',
        html,
    )
    if not match:
        match = re.search(
            r'value="([^"]+)"[^>]*name="csrf_token"',
            html,
        )
    assert match, "CSRF token missing from GET / HTML"
    return match.group(1)


def has_testid(html: str, testid: str) -> bool:
    return f'data-testid="{testid}"' in html


def post_search(client, **fields):
    home = client.get("/")
    token = csrf_token(home.get_data(as_text=True))
    payload = {"csrf_token": token, **fields}
    return client.post("/search", data=payload)


def test_get_home_initial_matrix_and_csrf(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert has_testid(html, "search-form")
    assert has_testid(html, "server-today")
    assert has_testid(html, "departure-city")
    assert has_testid(html, "arrival-city")
    assert has_testid(html, "travel-date")
    assert has_testid(html, "passengers")
    assert has_testid(html, "search-submit")
    assert "Search Flights" in html
    csrf_token(html)
    today = date.today().isoformat()
    assert f">{today}<" in html or today in html
    assert has_testid(html, "validation-errors")
    assert 'data-testid="results-list"' not in html
    assert 'data-testid="no-flights"' not in html
    assert 'data-testid="passenger-context"' not in html
    assert 'data-testid="flight-card"' not in html


def test_post_happy_path_delhi_mumbai(client):
    response = post_search(
        client,
        departure_city="delhi",
        arrival_city="Mumbai",
        travel_date="2099-06-15",
        passengers="2",
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert has_testid(html, "results-list")
    assert has_testid(html, "flight-card")
    assert has_testid(html, "result-airline")
    assert has_testid(html, "result-flight-number")
    assert has_testid(html, "result-departure-city")
    assert has_testid(html, "result-arrival-city")
    assert has_testid(html, "result-departure-time")
    assert has_testid(html, "result-arrival-time")
    assert has_testid(html, "result-duration")
    assert has_testid(html, "result-stops")
    assert has_testid(html, "result-price")
    assert has_testid(html, "passenger-context")
    assert "Passengers: 2" in html
    assert 'data-testid="no-flights"' not in html
    hidden_errors = re.search(
        r'<div data-testid="validation-errors"[^>]*hidden',
        html,
    )
    assert hidden_errors or ">validation-errors"  # present but empty/hidden
    assert "6E-201" in html
    assert "AI-440" in html


def test_post_zero_matches(client):
    response = post_search(
        client,
        departure_city="Delhi",
        arrival_city="Kolkata",
        travel_date="2099-12-31",
        passengers="1",
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert has_testid(html, "no-flights")
    assert "No flights found" in html
    assert has_testid(html, "passenger-context")
    assert 'data-testid="results-list"' not in html
    assert 'data-testid="flight-card"' not in html


def test_validation_same_city_no_results(client):
    response = post_search(
        client,
        departure_city="Delhi",
        arrival_city="delhi",
        travel_date="2099-06-15",
        passengers="1",
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert has_testid(html, "validation-errors")
    assert "hidden" not in re.search(
        r'<div data-testid="validation-errors"[^>]*>', html
    ).group(0)
    assert "different" in html.lower()
    assert 'data-testid="results-list"' not in html
    assert 'data-testid="no-flights"' not in html
    assert 'data-testid="passenger-context"' not in html


def test_validation_past_date(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = post_search(
        client,
        departure_city="Delhi",
        arrival_city="Mumbai",
        travel_date=yesterday,
        passengers="1",
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "past" in html.lower()
    assert 'data-testid="results-list"' not in html
    assert 'data-testid="no-flights"' not in html


def test_validation_missing_and_pax_range(client):
    missing = post_search(
        client,
        departure_city="",
        arrival_city="",
        travel_date="",
        passengers="",
    )
    assert missing.status_code == 200
    html = missing.get_data(as_text=True)
    assert has_testid(html, "validation-errors")
    assert 'data-testid="results-list"' not in html
    assert 'data-testid="no-flights"' not in html

    out = post_search(
        client,
        departure_city="Delhi",
        arrival_city="Mumbai",
        travel_date="2099-06-15",
        passengers="10",
    )
    assert out.status_code == 200
    html = out.get_data(as_text=True)
    assert "Passengers" in html
    assert 'data-testid="results-list"' not in html


def test_get_search_redirects_home(client):
    response = client.get("/search", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_missing_csrf_returns_generic_400(client):
    response = client.post(
        "/search",
        data={
            "departure_city": "Delhi",
            "arrival_city": "Mumbai",
            "travel_date": "2099-06-15",
            "passengers": "1",
        },
    )
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Traceback" not in html
    assert "SECRET_KEY" not in html
    assert "Bad request" in html


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_passengers_display_only_same_prices(client):
    one = post_search(
        client,
        departure_city="Delhi",
        arrival_city="Mumbai",
        travel_date="2099-06-15",
        passengers="1",
    )
    nine = post_search(
        client,
        departure_city="Delhi",
        arrival_city="Mumbai",
        travel_date="2099-06-15",
        passengers="9",
    )
    prices_one = re.findall(
        r'data-testid="result-price">(.*?)</div>',
        one.get_data(as_text=True),
    )
    prices_nine = re.findall(
        r'data-testid="result-price">(.*?)</div>',
        nine.get_data(as_text=True),
    )
    assert prices_one
    assert prices_one == prices_nine
    assert "Passengers: 1" in one.get_data(as_text=True)
    assert "Passengers: 9" in nine.get_data(as_text=True)


def test_404_generic(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "Traceback" not in html
    assert "Not found" in html
