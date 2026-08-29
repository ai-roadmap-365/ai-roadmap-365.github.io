"""Tests for the type-conversion demo, including what a 500 looks like.

The last two tests are the ones the lesson leans on: a validation failure is
a 422 that tells the caller exactly what to fix, and a bug in your code is a
500 that tells the caller nothing at all. Both are correct behaviour. The
difference is who the problem belongs to.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from type_demo import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_a_path_parameter_is_converted_to_the_declared_type(
    client: TestClient,
) -> None:
    body = client.get("/items/7").json()
    assert body == {"item_id": 7, "python_type": "int"}


def test_a_path_parameter_that_cannot_convert_is_422(client: TestClient) -> None:
    response = client.get("/items/seven")
    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["loc"] == ["path", "item_id"]
    assert detail["type"] == "int_parsing"
    assert detail["input"] == "seven"


def test_query_defaults_apply_when_nothing_is_sent(client: TestClient) -> None:
    body = client.get("/search", params={"q": "fastapi"}).json()
    assert body == {"q": "fastapi", "page": 1, "verbose": False, "sort": None}


def test_a_missing_required_query_parameter_is_422(client: TestClient) -> None:
    response = client.get("/search")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "q"]
    assert response.json()["detail"][0]["type"] == "missing"


def test_a_boolean_query_parameter_accepts_the_spellings_http_carries(
    client: TestClient,
) -> None:
    for spelling in ("true", "True", "1", "yes", "on"):
        body = client.get("/search", params={"q": "x", "verbose": spelling}).json()
        assert body["verbose"] is True
    for spelling in ("false", "0", "no", "off"):
        body = client.get("/search", params={"q": "x", "verbose": spelling}).json()
        assert body["verbose"] is False


def test_a_query_constraint_is_enforced(client: TestClient) -> None:
    response = client.get("/search", params={"q": "x", "sort": "a" * 17})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_long"


def test_an_unhandled_exception_becomes_a_500_with_no_traceback() -> None:
    """The client learns that it broke, and learns nothing else.

    ``raise_server_exceptions=False`` makes TestClient behave the way a real
    ASGI server does instead of re-raising the exception into the test. The
    body is the five-word default, and it contains no filename, no line
    number and no variable value.
    """
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/ratio/1/0")
    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert "ZeroDivisionError" not in response.text
    assert "Traceback" not in response.text
    assert "type_demo.py" not in response.text


def test_the_same_route_works_when_the_arguments_are_valid() -> None:
    with TestClient(app) as client:
        assert client.get("/ratio/3/4").json() == {"result": 0.75}
