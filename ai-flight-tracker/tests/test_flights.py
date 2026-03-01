from unittest.mock import patch


def test_flights_missing_partial_bbox(client):
    rv = client.get("/api/flights?lamin=40")
    assert rv.status_code == 400
    data = rv.get_json()
    assert "error" in data


def test_flights_invalid_bbox_order(client):
    rv = client.get("/api/flights?lamin=60&lamax=40&lomin=10&lomax=20")
    assert rv.status_code == 400


def test_flights_invalid_icao24(client):
    rv = client.get("/api/flights/ZZZZZZ")
    assert rv.status_code == 400
    data = rv.get_json()
    assert "error" in data


def test_flights_with_mock(client):
    mock_flights = [
        {"icao24": "abc123", "callsign": "TEST1", "origin_country": "DE",
         "lat": 48.0, "lon": 11.0, "altitude": 9000.0, "velocity": 250.0,
         "heading": 90.0, "on_ground": False, "last_contact": 1700000000}
    ]
    with patch("services.opensky.fetch_flights", return_value=mock_flights):
        rv = client.get("/api/flights?lamin=40&lamax=55&lomin=5&lomax=20")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "flights" in data
        assert data["count"] == 1
        assert data["flights"][0]["icao24"] == "abc123"


def test_flights_no_bbox(client):
    with patch("services.opensky.fetch_flights", return_value=[]):
        rv = client.get("/api/flights")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "flights" in data
