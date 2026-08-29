#!/usr/bin/env bash
# Tests for the Day 082 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This harness proves seven specific claims the lesson makes, and it proves
# them by running the application rather than by reading it:
#
#   * a valid create returns 201 and exactly the response-model shape;
#   * an invalid body returns 422 whose structured detail NAMES the field;
#   * a missing resource returns 404 with a detail string, not a traceback;
#   * DELETE returns 204 with an empty body and the resource is then gone;
#   * the response never contains the internal owner_token — the leak check,
#     asserted by absence, because a leak is invisible until somebody looks;
#   * the OpenAPI schema is generated and contains every declared path;
#   * the injected fake storage means no real file was written anywhere.
#
# And an eighth, which is this week's rule made mechanical: the reference
# suite runs behind a guard that raises on any outbound connection, and
# section 7 below proves that guard is not decorative by making a test trip
# it on purpose.
#
# Everything runs in-process through FastAPI's TestClient. No server is
# started, no port is bound, no socket is opened. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

# Resolve pytest: an explicit override, then this lab's .venv, then whatever
# is on PATH. Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

# The Python that owns that pytest is the one with fastapi installed.
python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import fastapi" >/dev/null 2>&1; then
  echo "FAIL: fastapi is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 082 — Serve Something Real"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
from importlib.metadata import version
for name in ("fastapi", "pydantic", "starlette", "uvicorn", "httpx", "pytest"):
    print(f"{name}=={version(name)}")
PY
)"
printf '%s\n' "${versions}" | sed 's/^/     /'

for pin in "fastapi==0.139.2" "uvicorn==0.51.0" "httpx==0.28.1" "pytest==9.1.1"; do
  case "${versions}" in
    *"${pin}"*) check "installed ${pin} matches requirements/requirements.txt" "yes" ;;
    *) check "installed ${pin} matches requirements/requirements.txt" "no" ;;
  esac
done

# pydantic is not requested directly — it arrives because FastAPI depends on
# it — so this check confirms the pin matches what actually got installed
# rather than what somebody assumed.
case "${versions}" in
  *"pydantic==2.13.4"*) check "pydantic 2.13.4 arrived as a FastAPI dependency" "yes" ;;
  *) check "pydantic 2.13.4 arrived as a FastAPI dependency" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. The reference suite passes"
# --------------------------------------------------------------------------

examples_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_exit=$?
if [ "${examples_exit}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0 (got ${examples_exit})" "no"
  printf '%s\n' "${examples_out}" | tail -30
fi

case "${examples_out}" in
  *"42 passed"*) check "pytest examples reports 42 passed" "yes" ;;
  *) check "pytest examples reports 42 passed (got: $(printf '%s' "${examples_out}" | tail -1))" "no" ;;
esac

# The named assertions the lesson promises really exist and really run.
collected="$(cd "${lab_dir}" && "${pytest_bin}" examples --collect-only -q 2>&1)"
for test_id in \
  "test_api.py::test_a_valid_create_returns_201" \
  "test_api.py::test_an_empty_title_is_422_and_the_detail_names_the_field" \
  "test_api.py::test_a_missing_bookmark_is_404_with_a_detail_and_no_traceback" \
  "test_api.py::test_delete_returns_204_with_an_empty_body" \
  "test_api.py::test_the_response_does_not_contain_the_internal_owner_token" \
  "test_api.py::test_the_openapi_schema_contains_every_declared_path" \
  "test_api.py::test_no_file_was_written_anywhere_near_this_lab" \
  "test_type_demo.py::test_an_unhandled_exception_becomes_a_500_with_no_traceback"
do
  case "${collected}" in
    *"${test_id}"*) check "collection finds ${test_id}" "yes" ;;
    *) check "collection finds ${test_id}" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "3. The seven claims, verified independently of pytest"
# --------------------------------------------------------------------------

# This block drives the same application through TestClient from a plain
# script, so the checks do not depend on the lab's own test file being
# correct. It prints one PASS/FAIL line per claim and exits non-zero if any
# claim fails.
claims_out="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY' 2>&1
import itertools
import json
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path

warnings.filterwarnings(
    "ignore", message="Using `httpx` with `starlette.testclient` is deprecated"
)

sys.path.insert(0, str(Path.cwd()))

import api
from fastapi.testclient import TestClient
from storage import InMemoryStorage

store = InMemoryStorage()
counter = itertools.count(1)
api.app.dependency_overrides[api.get_storage] = lambda: store
api.app.dependency_overrides[api.get_now] = lambda: datetime(2026, 7, 19, 9, 30, tzinfo=UTC)
api.app.dependency_overrides[api.get_new_id] = lambda: f"bm-{next(counter):04d}"
api.app.dependency_overrides[api.get_owner_token] = lambda: "secret-owner-token"
client = TestClient(api.app)

VALID = {
    "title": "The FastAPI documentation",
    "url": "https://fastapi.tiangolo.com/",
    "tags": ["python", "web"],
}

failed = 0


def claim(label, ok):
    global failed
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        failed += 1


created = client.post("/bookmarks", json=VALID)
body = created.json()
claim("create returns 201", created.status_code == 201)
claim(
    "create returns exactly the response-model shape",
    set(body) == {"id", "title", "url", "tags", "created_at"},
)
claim("create sets a Location header", created.headers.get("location") == "/bookmarks/bm-0001")

bad = client.post("/bookmarks", json={**VALID, "title": ""})
detail = bad.json().get("detail", [{}])
claim("an invalid body returns 422", bad.status_code == 422)
claim(
    "the 422 detail names the offending field",
    detail[0].get("loc") == ["body", "title"] and detail[0].get("type") == "string_too_short",
)

missing = client.get("/bookmarks/no-such-id")
claim("a missing resource returns 404", missing.status_code == 404)
claim(
    "the 404 body is a detail string, not a traceback",
    isinstance(missing.json().get("detail"), str)
    and "Traceback" not in missing.text
    and "storage.py" not in missing.text,
)

deleted = client.delete("/bookmarks/bm-0001")
claim("delete returns 204", deleted.status_code == 204)
claim("the 204 body is empty", deleted.content == b"")
claim("the resource is gone afterwards", client.get("/bookmarks/bm-0001").status_code == 404)

again = client.post("/bookmarks", json=VALID)
new_id = again.json()["id"]
stored = store.get(new_id)
claim("the server really did store the internal field", stored.owner_token == "secret-owner-token")
claim("the response body has no owner_token key", "owner_token" not in again.json())
claim("the response text does not contain the secret", "secret-owner-token" not in again.text)

schema = client.get("/openapi.json").json()
claim("the OpenAPI schema is generated", schema.get("openapi", "").startswith("3."))
claim(
    "the schema contains every declared path",
    set(schema["paths"]) == {"/health", "/bookmarks", "/bookmarks/{bookmark_id}"},
)
claim(
    "the schema records the chosen status codes",
    "201" in schema["paths"]["/bookmarks"]["post"]["responses"]
    and "204" in schema["paths"]["/bookmarks/{bookmark_id}"]["delete"]["responses"],
)
claim(
    "the public output schema has no owner_token",
    "owner_token" not in schema["components"]["schemas"]["BookmarkOut"]["properties"],
)

claim("the injected storage holds the records", [b.id for b in store.all()] == [new_id])
claim(
    "no bookmarks.json was written anywhere in the lab",
    not any(Path.cwd().parent.rglob("bookmarks.json")),
)

sys.exit(1 if failed else 0)
PY
)"
claims_exit=$?
printf '%s\n' "${claims_out}" | sed 's/^/     /'
if [ "${claims_exit}" -eq 0 ]; then
  check "all independent claim checks passed" "yes"
else
  check "all independent claim checks passed (script exit ${claims_exit})" "no"
fi
claim_count="$(printf '%s\n' "${claims_out}" | grep -c '^PASS ' || true)"
if [ "${claim_count}" -eq 19 ]; then
  check "all 19 claims were actually evaluated" "yes"
else
  check "all 19 claims were actually evaluated (counted ${claim_count})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The demo script runs and prints what the lesson quotes"
# --------------------------------------------------------------------------

demo_out="$(cd "${lab_dir}" && "${python_bin}" examples/demo.py 2>&1)"
demo_exit=$?
if [ "${demo_exit}" -eq 0 ]; then
  check "examples/demo.py exits 0" "yes"
else
  check "examples/demo.py exits 0 (got ${demo_exit})" "no"
fi

for fragment in \
  'Location: /bookmarks/bm-0001' \
  '"type": "string_too_short"' \
  '"type": "url_parsing"' \
  '"type": "extra_forbidden"' \
  '"detail": "No bookmark with id '"'"'nope'"'"'"' \
  'owner_token in the response body? False' \
  'openapi version : 3.1.0'
do
  case "${demo_out}" in
    *"${fragment}"*) check "demo output contains: ${fragment}" "yes" ;;
    *) check "demo output contains: ${fragment}" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "5. The starter is runnable before you start, and honest about it"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "pytest starter exits 0 with the exercises unfinished" "yes"
else
  check "pytest starter exits 0 with the exercises unfinished (got ${starter_exit})" "no"
fi
case "${starter_out}" in
  *"1 passed, 9 skipped"*) check "the starter has 1 worked test and 9 skipped exercises" "yes" ;;
  *) check "the starter has 1 worked test and 9 skipped exercises" "no" ;;
esac

schema_out="$(cd "${lab_dir}" && "${python_bin}" starter/schema.py 2>&1)"
schema_exit=$?
if [ "${schema_exit}" -eq 0 ]; then
  check "starter/schema.py exits 0" "yes"
else
  check "starter/schema.py exits 0 (got ${schema_exit})" "no"
fi
case "${schema_out}" in
  *"No BookmarkOut schema yet"*)
    check "starter/schema.py reports the unfinished state honestly" "yes" ;;
  *) check "starter/schema.py reports the unfinished state honestly" "no" ;;
esac

# The starter really is the naive version the exercises fix: one shared model
# that carries the internal field into the public schema.
case "${schema_out}" in
  *"Component schemas: Bookmark,"*)
    check "the starter still has one shared model (Exercise 2 splits it)" "yes" ;;
  *) check "the starter still has one shared model (Exercise 2 splits it)" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "6. The starter suite is not vacuous — it fails on a broken app"
# --------------------------------------------------------------------------

# Copy the reference implementation in as `app.py`, un-skip everything, and
# demand that the starter's own suite goes green. A suite that cannot tell a
# finished application from an unfinished one is worth nothing.
work="$(mktemp -d "${TMPDIR:-/tmp}/day082-solved.XXXXXX")"
cp "${lab_dir}/starter/test_app.py" "${lab_dir}/starter/conftest.py" \
   "${lab_dir}/starter/pytest.ini" "${work}/"
cp "${lab_dir}/examples/models.py" "${lab_dir}/examples/storage.py" "${work}/"
cp "${lab_dir}/examples/api.py" "${work}/app.py"
# The starter's conftest clears a global the finished app does not have.
"${python_bin}" - "${work}/conftest.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("    app.BOOKMARKS.clear()", "    getattr(app, 'BOOKMARKS', {}).clear()")
path.write_text(text, encoding="utf-8")
PY
"${python_bin}" - "${work}/test_app.py" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = [
    line
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not re.match(r"^@pytest\.mark\.skip", line)
]
path.write_text("".join(lines), encoding="utf-8")
PY

solved_out="$(cd "${work}" && "${pytest_bin}" . -q 2>&1)"
solved_exit=$?
if [ "${solved_exit}" -eq 0 ]; then
  check "the starter suite goes fully green against the finished application" "yes"
else
  check "the starter suite goes fully green against the finished application (exit ${solved_exit})" "no"
  printf '%s\n' "${solved_out}" | tail -20
fi
case "${solved_out}" in
  *"10 passed"*) check "all 10 starter tests pass once the exercises are done" "yes" ;;
  *) check "all 10 starter tests pass once the exercises are done" "no" ;;
esac

# Now break exactly one thing — remove the response_model that stops the leak
# — and demand that the leak check FAILS. This is the check that proves the
# leak assertion is doing work.
sed -i.bak 's/    response_model=BookmarkOut,//' "${work}/app.py"
rm -f "${work}/app.py.bak"
leak_out="$(cd "${work}" && "${pytest_bin}" . -q 2>&1)"
leak_exit=$?
if [ "${leak_exit}" -ne 0 ]; then
  check "removing response_model makes the suite FAIL (exit ${leak_exit}, not 0)" "yes"
else
  check "removing response_model makes the suite FAIL — it did not, so the leak check is vacuous" "no"
fi
case "${leak_out}" in
  *"test_the_response_never_contains_the_internal_owner_token"*)
    check "the failing run names the leak check by test id" "yes" ;;
  *) check "the failing run names the leak check by test id" "no" ;;
esac
rm -rf "${work}"

# --------------------------------------------------------------------------
echo
echo "7. Nothing opened a socket — and the guard that says so is real"
# --------------------------------------------------------------------------

# The reference suite ran behind an autouse guard that raises on any outbound
# connection. Prove the guard is armed by writing one test that deliberately
# trips it, and demanding a failure.
guard="$(mktemp -d "${TMPDIR:-/tmp}/day082-guard.XXXXXX")"
cp "${lab_dir}/examples/conftest.py" "${lab_dir}/examples/models.py" \
   "${lab_dir}/examples/storage.py" "${lab_dir}/examples/api.py" \
   "${lab_dir}/examples/pytest.ini" "${guard}/"
cat > "${guard}/test_guard.py" <<'PY'
"""One test that deliberately reaches for the network. It must fail."""

import socket


def test_this_one_should_be_stopped_by_the_guard():
    socket.create_connection(("127.0.0.1", 9), timeout=0.1)
PY
guard_out="$(cd "${guard}" && "${pytest_bin}" . -q 2>&1)"
guard_exit=$?
if [ "${guard_exit}" -ne 0 ]; then
  check "a test that tries to connect is stopped (exit ${guard_exit}, not 0)" "yes"
else
  check "a test that tries to connect is stopped — it was not, so the guard is decorative" "no"
fi
case "${guard_out}" in
  *"NetworkAccessAttempted"*)
    check "the guard raises NetworkAccessAttempted naming the address" "yes" ;;
  *) check "the guard raises NetworkAccessAttempted naming the address" "no" ;;
esac
rm -rf "${guard}"

# The guard was armed for the reference run too, and that run was green.
case "${examples_out}" in
  *NetworkAccessAttempted*)
    check "no test in the reference suite tripped the network guard" "no" ;;
  *) check "no test in the reference suite tripped the network guard" "yes" ;;
esac

# Belt and braces: no lab source asks for a real network client or binds a port.
if grep -rqE 'requests\.get|urlopen|uvicorn\.run|\.bind\(|httpx\.(get|post|Client)' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a connection or binds a port" "no"
else
  check "no lab source opens a connection or binds a port" "yes"
fi

# --------------------------------------------------------------------------
echo
echo "8. Nothing was written to disk"
# --------------------------------------------------------------------------

if find "${lab_dir}" -name 'bookmarks.json' -print -quit 2>/dev/null | grep -q .; then
  check "no bookmarks.json anywhere under the lab after a full run" "no"
else
  check "no bookmarks.json anywhere under the lab after a full run" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
