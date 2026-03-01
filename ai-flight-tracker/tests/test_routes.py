import json


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_get_routes(client):
    rv = client.get("/api/routes")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "routes" in data
    assert len(data["routes"]) > 0
    # Priority routes first
    first = data["routes"][0]
    assert first["is_priority"] is True
    assert "route_code" in first
    assert "origin" in first
    assert "destination" in first


def test_get_route_detail(client):
    rv = client.get("/api/route/DAC-WAW")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["route_code"] == "DAC-WAW"
    assert "pricing" in data
    assert "last_minute" in data["pricing"]


def test_get_route_not_found(client):
    rv = client.get("/api/route/ZZZ-ZZZ")
    assert rv.status_code == 404
    data = rv.get_json()
    assert "error" in data


def test_search_routes(client):
    rv = client.get("/api/search?origin=Dhaka")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "results" in data
    assert data["count"] == len(data["results"])
    for r in data["results"]:
        assert "Dhaka" in r["origin"] or "DAC" in r["origin"]


def test_search_no_params(client):
    rv = client.get("/api/search")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "results" in data
    assert len(data["results"]) > 0


def test_search_max_stops(client):
    rv = client.get("/api/search?max_stops=0")
    assert rv.status_code == 200
    data = rv.get_json()
    for r in data["results"]:
        assert r["num_stops"] == 0
