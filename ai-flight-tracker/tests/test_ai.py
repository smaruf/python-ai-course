from unittest.mock import patch
from services.ai import _route_intent, tool_list_routes, tool_search_routes


def test_list_routes_tool():
    result = tool_list_routes()
    assert isinstance(result, dict)
    assert "DAC-WAW" in result
    assert "base_price" in result["DAC-WAW"]


def test_search_routes_tool():
    result = tool_search_routes(origin="DAC")
    assert isinstance(result, list)
    for r in result:
        assert "DAC" in r["route_code"]


def test_intent_route_search():
    intent = _route_intent("What are the cheapest flights from Dhaka?")
    assert intent["tool"] in ("search_routes", "list_routes")
    assert "result" in intent


def test_intent_list_all():
    intent = _route_intent("Show me all routes")
    assert intent["tool"] == "list_routes"
    assert isinstance(intent["result"], dict)


def test_aviation_ask_no_ollama(client):
    with patch("services.ai.ask") as mock_ask:
        mock_ask.return_value = "There are flights from Dhaka to Warsaw."
        rv = client.post(
            "/api/aviation/ask",
            json={"question": "What flights go from Dhaka to Warsaw?"}
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert "answer" in data
        assert len(data["answer"]) > 0


def test_aviation_ask_missing_question(client):
    rv = client.post("/api/aviation/ask", json={})
    assert rv.status_code == 400
    data = rv.get_json()
    assert "error" in data


def test_aviation_ask_too_long(client):
    rv = client.post("/api/aviation/ask", json={"question": "x" * 501})
    assert rv.status_code == 400


def test_aviation_ask_not_json(client):
    rv = client.post("/api/aviation/ask", data="plain text")
    assert rv.status_code == 400
