"""Your exercise suite. One test passes now; nine are waiting for you.

Run it:

    .venv/bin/pytest starter -q

Each skipped test names the exercise in `app.py` that makes it pass. Do the
exercise, delete that test's `@pytest.mark.skip(...)` line, rerun. When all
nine are green, `starter/app.py` does what `examples/api.py` does, and you
wrote it.

Everything here goes through `TestClient`, which drives the application in
this process. No server, no port, no socket — `conftest.py` arms a guard
that would raise if anything tried.
"""

from __future__ import annotations

import pytest
from app import app
from fastapi.testclient import TestClient

VALID = {
    "title": "The FastAPI documentation",
    "url": "https://fastapi.tiangolo.com/",
    "tags": ["python", "web"],
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_is_ok_and_counts_bookmarks(client: TestClient) -> None:
    """This one passes already. It is here so you always have a green
    baseline: if it ever fails, the problem is your setup, not your code."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "bookmarks": 0}


@pytest.mark.skip(reason="Exercise 1: constrain title and make url an HttpUrl")
def test_an_empty_title_is_422_naming_the_field(client: TestClient) -> None:
    response = client.post("/bookmarks", json={**VALID, "title": ""})
    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "title"]
    assert detail["type"] == "string_too_short"


@pytest.mark.skip(reason="Exercise 1: constrain title and make url an HttpUrl")
def test_a_non_url_is_422_naming_the_field(client: TestClient) -> None:
    response = client.post("/bookmarks", json={**VALID, "url": "not a url"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "url"]


@pytest.mark.skip(reason="Exercise 2: split the model and add response_model")
def test_the_response_never_contains_the_internal_owner_token(
    client: TestClient,
) -> None:
    """The leak check. A leak is invisible until somebody asserts on it."""
    response = client.post("/bookmarks", json=VALID)
    assert "owner_token" not in response.json()
    assert "owner_token" not in response.text


@pytest.mark.skip(reason="Exercise 2: extra='forbid' on the create model")
def test_a_client_cannot_choose_its_own_id(client: TestClient) -> None:
    response = client.post("/bookmarks", json={**VALID, "id": "admin"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "id"]


@pytest.mark.skip(reason="Exercise 3: 201 Created and a Location header")
def test_create_returns_201_and_a_location_header(client: TestClient) -> None:
    response = client.post("/bookmarks", json=VALID)
    assert response.status_code == 201
    location = response.headers["location"]
    assert location.startswith("/bookmarks/")
    assert client.get(location).status_code == 200


@pytest.mark.skip(reason="Exercise 4: tag and limit query parameters")
def test_listing_filters_by_tag_and_validates_limit(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    client.post("/bookmarks", json={**VALID, "title": "Cron", "tags": ["scheduling"]})

    filtered = client.get("/bookmarks", params={"tag": "scheduling"}).json()
    assert [item["title"] for item in filtered] == ["Cron"]

    assert client.get("/bookmarks", params={"limit": 0}).status_code == 422


@pytest.mark.skip(reason="Exercise 5: 404 instead of a KeyError")
def test_a_missing_bookmark_is_404_and_not_a_traceback(client: TestClient) -> None:
    response = client.get("/bookmarks/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "Traceback" not in response.text


@pytest.mark.skip(reason="Exercise 6: PATCH and DELETE")
def test_patch_then_delete(client: TestClient) -> None:
    created = client.post("/bookmarks", json=VALID).json()
    bookmark_id = created["id"]

    patched = client.patch(f"/bookmarks/{bookmark_id}", json={"title": "Renamed"})
    assert patched.status_code == 200
    assert patched.json()["title"] == "Renamed"
    assert patched.json()["url"] == "https://fastapi.tiangolo.com/"

    deleted = client.delete(f"/bookmarks/{bookmark_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/bookmarks/{bookmark_id}").status_code == 404


@pytest.mark.skip(reason="Exercise 8: the generated contract")
def test_the_openapi_schema_declares_every_path_and_no_secret(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()
    assert set(schema["paths"]) >= {
        "/health",
        "/bookmarks",
        "/bookmarks/{bookmark_id}",
    }
    assert "201" in schema["paths"]["/bookmarks"]["post"]["responses"]
    assert "204" in schema["paths"]["/bookmarks/{bookmark_id}"]["delete"]["responses"]
    out = schema["components"]["schemas"]["BookmarkOut"]["properties"]
    assert "owner_token" not in out
