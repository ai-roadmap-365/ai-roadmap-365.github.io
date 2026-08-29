"""The reference suite for the bookmarks API.

Every test here drives the application through ``TestClient``. That class
wraps httpx and speaks to the ASGI app object directly, in this process, in
this thread's event loop. There is no server, no port, no socket, and no
race between "started" and "ready". ``conftest.py`` arms a guard that would
raise if anything did try to connect; the suite is green, so nothing did.

Three dependencies are overridden for every test — storage, the clock and
the id source — via ``app.dependency_overrides``. That dictionary maps the
production dependency function to the one you want instead, and FastAPI
consults it on every request. Nothing inside ``api.py`` is patched, and the
handlers cannot tell the difference; they simply receive what they asked
for.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import api
import pytest
from fastapi.testclient import TestClient
from storage import InMemoryStorage

FROZEN_NOW = datetime(2026, 7, 19, 9, 30, tzinfo=UTC)
FROZEN_NOW_JSON = "2026-07-19T09:30:00Z"


@pytest.fixture
def storage() -> InMemoryStorage:
    """The fake the application will be given. A real, correct dictionary."""
    return InMemoryStorage()


@pytest.fixture
def client(
    storage: InMemoryStorage, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """A TestClient wired to the fake storage, a frozen clock and counted ids."""
    # If the production file storage is ever constructed during a test, that
    # is a bug in the wiring and this makes it loud rather than silent.
    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("the real JsonFileStorage was constructed in a test")

    monkeypatch.setattr(api, "JsonFileStorage", refuse)

    counter = itertools.count(1)
    api.app.dependency_overrides[api.get_storage] = lambda: storage
    api.app.dependency_overrides[api.get_now] = lambda: FROZEN_NOW
    api.app.dependency_overrides[api.get_new_id] = lambda: f"bm-{next(counter):04d}"
    api.app.dependency_overrides[api.get_owner_token] = lambda: "secret-owner-token"
    with TestClient(api.app) as test_client:
        yield test_client
    api.app.dependency_overrides.clear()


VALID = {
    "title": "The FastAPI documentation",
    "url": "https://fastapi.tiangolo.com/",
    "tags": ["python", "web"],
}


# --------------------------------------------------------------------------
# Creating
# --------------------------------------------------------------------------


def test_a_valid_create_returns_201(client: TestClient) -> None:
    response = client.post("/bookmarks", json=VALID)
    assert response.status_code == 201


def test_a_valid_create_returns_the_response_model_shape(client: TestClient) -> None:
    body = client.post("/bookmarks", json=VALID).json()
    assert set(body) == {"id", "title", "url", "tags", "created_at"}
    assert body["id"] == "bm-0001"
    assert body["title"] == "The FastAPI documentation"
    assert body["url"] == "https://fastapi.tiangolo.com/"
    assert body["tags"] == ["python", "web"]
    assert body["created_at"] == FROZEN_NOW_JSON


def test_create_sets_a_location_header_naming_the_new_resource(
    client: TestClient,
) -> None:
    response = client.post("/bookmarks", json=VALID)
    assert response.headers["location"] == "/bookmarks/bm-0001"
    # And the header is not decorative: it addresses something real.
    assert client.get(response.headers["location"]).status_code == 200


def test_the_id_is_server_generated_and_a_client_cannot_choose_it(
    client: TestClient,
) -> None:
    response = client.post("/bookmarks", json={**VALID, "id": "admin"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "id"]


# --------------------------------------------------------------------------
# Validation: 422 and its structured detail
# --------------------------------------------------------------------------


def test_an_empty_title_is_422_and_the_detail_names_the_field(
    client: TestClient,
) -> None:
    response = client.post("/bookmarks", json={**VALID, "title": ""})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["loc"] == ["body", "title"]
    assert detail[0]["type"] == "string_too_short"


def test_a_non_url_is_422_and_the_detail_names_the_field(client: TestClient) -> None:
    response = client.post("/bookmarks", json={**VALID, "url": "not a url"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["loc"] == ["body", "url"]
    assert "url" in detail[0]["type"]


def test_a_missing_required_field_is_422(client: TestClient) -> None:
    response = client.post("/bookmarks", json={"title": "No URL here"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"] == ["body", "url"]


def test_two_bad_fields_produce_two_entries_in_one_response(
    client: TestClient,
) -> None:
    """Validation reports everything wrong at once, not the first thing."""
    response = client.post("/bookmarks", json={"title": "", "url": "nope"})
    assert response.status_code == 422
    locs = [tuple(item["loc"]) for item in response.json()["detail"]]
    assert ("body", "title") in locs
    assert ("body", "url") in locs


def test_a_rejected_body_is_never_stored(
    client: TestClient, storage: InMemoryStorage
) -> None:
    client.post("/bookmarks", json={**VALID, "title": ""})
    assert storage.all() == []


def test_an_out_of_range_query_parameter_is_422(client: TestClient) -> None:
    response = client.get("/bookmarks", params={"limit": 0})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "limit"]


def test_a_non_numeric_query_parameter_is_422(client: TestClient) -> None:
    response = client.get("/bookmarks", params={"limit": "many"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "int_parsing"


# --------------------------------------------------------------------------
# The leak check — this is the one worth reading twice
# --------------------------------------------------------------------------


def test_the_response_does_not_contain_the_internal_owner_token(
    client: TestClient, storage: InMemoryStorage
) -> None:
    response = client.post("/bookmarks", json=VALID)

    # The server really did store the secret ...
    stored = storage.get("bm-0001")
    assert stored is not None
    assert stored.owner_token == "secret-owner-token"

    # ... and it is absent from the response, by key and by raw text.
    assert "owner_token" not in response.json()
    assert "secret-owner-token" not in response.text


def test_no_endpoint_leaks_the_internal_field(client: TestClient) -> None:
    """Every route that returns a bookmark is checked, not just create."""
    client.post("/bookmarks", json=VALID)
    for response in (
        client.get("/bookmarks"),
        client.get("/bookmarks/bm-0001"),
        client.patch("/bookmarks/bm-0001", json={"title": "Renamed"}),
    ):
        assert response.status_code == 200
        assert "owner_token" not in response.text
        assert "secret-owner-token" not in response.text


def test_the_openapi_schema_does_not_advertise_the_internal_field(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()
    assert "owner_token" not in schema["components"]["schemas"]["BookmarkOut"][
        "properties"
    ]


# --------------------------------------------------------------------------
# Reading, filtering, updating, deleting
# --------------------------------------------------------------------------


def test_get_one_returns_what_was_created(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    body = client.get("/bookmarks/bm-0001").json()
    assert body["title"] == "The FastAPI documentation"


def test_a_missing_bookmark_is_404_with_a_detail_and_no_traceback(
    client: TestClient,
) -> None:
    response = client.get("/bookmarks/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "No bookmark with id 'does-not-exist'"}
    assert "Traceback" not in response.text
    assert "File \"" not in response.text


def test_listing_returns_every_bookmark(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    client.post("/bookmarks", json={**VALID, "title": "Second", "tags": ["python"]})
    assert len(client.get("/bookmarks").json()) == 2


def test_listing_filters_by_tag(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    client.post(
        "/bookmarks", json={**VALID, "title": "Second", "tags": ["scheduling"]}
    )
    body = client.get("/bookmarks", params={"tag": "scheduling"}).json()
    assert [item["title"] for item in body] == ["Second"]


def test_listing_respects_the_limit(client: TestClient) -> None:
    for index in range(5):
        client.post("/bookmarks", json={**VALID, "title": f"Item {index}"})
    assert len(client.get("/bookmarks", params={"limit": 2}).json()) == 2


def test_patch_changes_only_the_fields_that_were_sent(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    body = client.patch("/bookmarks/bm-0001", json={"title": "Renamed"}).json()
    assert body["title"] == "Renamed"
    assert body["url"] == "https://fastapi.tiangolo.com/"
    assert body["tags"] == ["python", "web"]


def test_patch_validates_too(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    response = client.patch("/bookmarks/bm-0001", json={"title": ""})
    assert response.status_code == 422


def test_patching_a_missing_bookmark_is_404(client: TestClient) -> None:
    assert client.patch("/bookmarks/nope", json={"title": "x"}).status_code == 404


def test_delete_returns_204_with_an_empty_body(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    response = client.delete("/bookmarks/bm-0001")
    assert response.status_code == 204
    assert response.content == b""


def test_after_delete_the_bookmark_is_gone(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    client.delete("/bookmarks/bm-0001")
    assert client.get("/bookmarks/bm-0001").status_code == 404
    assert client.get("/bookmarks").json() == []


def test_deleting_a_missing_bookmark_is_404(client: TestClient) -> None:
    assert client.delete("/bookmarks/nope").status_code == 404


def test_health_reports_the_count(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    assert client.get("/health").json() == {"status": "ok", "bookmarks": 1}


# --------------------------------------------------------------------------
# The generated contract
# --------------------------------------------------------------------------


def test_the_openapi_schema_is_generated(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Bookmarks API"
    assert schema["info"]["version"] == "1.0.0"
    assert schema["openapi"].startswith("3.")


def test_the_openapi_schema_contains_every_declared_path(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert set(paths) == {"/health", "/bookmarks", "/bookmarks/{bookmark_id}"}
    assert set(paths["/bookmarks"]) == {"get", "post"}
    assert set(paths["/bookmarks/{bookmark_id}"]) == {"get", "patch", "delete"}


def test_the_schema_records_the_status_codes_the_handlers_declared(
    client: TestClient,
) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "201" in paths["/bookmarks"]["post"]["responses"]
    assert "204" in paths["/bookmarks/{bookmark_id}"]["delete"]["responses"]
    assert "404" in paths["/bookmarks/{bookmark_id}"]["get"]["responses"]
    assert "422" in paths["/bookmarks"]["post"]["responses"]


def test_the_schema_records_the_validation_constraints(client: TestClient) -> None:
    create = client.get("/openapi.json").json()["components"]["schemas"][
        "BookmarkCreate"
    ]
    assert create["properties"]["title"]["minLength"] == 1
    assert create["properties"]["title"]["maxLength"] == 80
    assert create["required"] == ["title", "url"]


def test_the_interactive_documentation_is_served(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200


# --------------------------------------------------------------------------
# The boundary really was injected
# --------------------------------------------------------------------------


def test_the_injected_storage_is_the_one_the_handlers_used(
    client: TestClient, storage: InMemoryStorage
) -> None:
    client.post("/bookmarks", json=VALID)
    assert [b.id for b in storage.all()] == ["bm-0001"]


def test_no_file_was_written_anywhere_near_this_lab(client: TestClient) -> None:
    client.post("/bookmarks", json=VALID)
    lab_dir = Path(__file__).resolve().parent.parent
    assert not (lab_dir / "bookmarks.json").exists()
    assert not (lab_dir / "examples" / "bookmarks.json").exists()
    assert not (Path.cwd() / "bookmarks.json").exists()


def test_the_production_dependency_would_have_touched_a_file() -> None:
    """The control: without the override, ``get_storage`` builds file storage.

    Called directly here — not through a request — so nothing is written.
    """
    from storage import JsonFileStorage

    assert isinstance(api.get_storage(), JsonFileStorage)
