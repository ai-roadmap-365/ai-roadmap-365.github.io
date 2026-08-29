# Dependencies for the Day 082 lab

Five packages, all free and open source, all installed from the Python
Package Index with `pip`, all running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `fastapi` | `0.139.2` | The web framework the lesson is about. It reads your type annotations and turns them into request parsing, validation, serialization and a machine-readable OpenAPI schema. |
| `uvicorn` | `0.51.0` | The ASGI server that runs the application for real. The lab's tests do not use it — they use `TestClient` — but the README shows the command, because an application you can only test is not an application you can ship. |
| `httpx` | `0.28.1` | The HTTP client library `TestClient` is built on. You never call it directly; installing it is what makes `from fastapi.testclient import TestClient` work. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new today except what it is pointed at. |
| `pydantic` | `2.13.4` | Not requested directly — **it arrives because FastAPI depends on it**, and it is pinned here so that the validation messages you see match the captured output. It is the piece that makes an annotation do work at runtime. |

## Why pydantic is pinned even though nobody asked for it

`pip install fastapi` installs pydantic whether you name it or not. Leaving
it unpinned means a future pydantic release could change an error `type`
string — `string_too_short`, `url_parsing`, `int_parsing` — and the lab's
assertions, which check those strings, would fail for reasons that have
nothing to do with your code.

The pinned number was read from the installed package rather than assumed:

```bash
.venv/bin/python3 -c "from importlib.metadata import version; print(version('pydantic'))"
```

On the authoring machine, on 19 July 2026, that printed `2.13.4`, and the
first section of `tests/run_tests.sh` reprints every installed version and
compares it against this file — so a mismatch is reported rather than
discovered later as a mysterious failure.

`starlette` (version 1.3.1 here) also arrives as a FastAPI dependency and is
deliberately **not** pinned: FastAPI itself constrains which versions it
accepts, and pinning it separately is how you eventually get an unsolvable
dependency conflict.

## Licences

FastAPI, Starlette, pydantic, uvicorn, httpx and pytest are all distributed
under the MIT licence, stated on each project's own documentation site. Every
one is maintained in the open, costs nothing, and needs no account, no key
and no signup — personally or commercially.

## One-time install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import fastapi, pydantic; print(fastapi.__version__, pydantic.VERSION)"
```

Expect `0.139.2 2.13.4`. Day 43 covered `python3 -m venv` in full; this is
the same pattern. The environment lives in `.venv/` inside the lab, is
already excluded from version control, and can be deleted at any time with
`rm -rf .venv`.

## Network

Installing needs the network, once. **Nothing else in this lab does.** The
tests drive the application in-process through `TestClient`, and the
reference suite runs behind a guard that raises if anything tries to open a
connection — section 7 of `tests/run_tests.sh` proves that guard is armed by
making a test trip it deliberately.

## Running without a lab-local environment

If you already have these packages available in an environment you have
activated, the test runner will find `pytest` on your `PATH`. You can also
point it at a specific binary:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The runner uses the `python3` that sits beside that `pytest`, because that is
the interpreter with FastAPI installed. If FastAPI is not importable from it,
the runner says so and stops rather than skipping checks quietly.

## A note you will see in your own output

With this pinned combination, `starlette` 1.3.1 emits one deprecation notice
saying a future release prefers `httpx2` over `httpx`. Everything works —
all 42 reference tests pass on it — and the two `pytest.ini` files filter the
notice so the captured output stays readable. `../troubleshooting.md`
explains it rather than pretending it is not there.
