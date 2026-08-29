# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, which downloads pandas and pytest from
  PyPI into this lab's own `.venv`. Everything after that runs completely
  offline.
- Binds **one** local socket per test that uses it: `mock_server.py` opens
  a `ThreadingHTTPServer` on `127.0.0.1` with port `0`, which asks the
  operating system for any free port rather than claiming a fixed one.
  Nothing is reachable from outside the machine — `127.0.0.1` is loopback
  only — and every server is shut down, closed, and its thread joined in
  the `finally` block of `serve_mock_api`, including when a test fails.
  When the suite finishes, nothing from this lab is listening.
- Writes only inside `.venv` (created by you), transient `__pycache__`
  and `.pytest_cache` directories the harness removes before and after
  every run, and `tmp_path` directories pytest creates and deletes itself.
  No file is written outside this lab's own directory.
- Never needs `sudo`, a credential, an API key, or an account of any kind.

## Why a mock server rather than a real one

Every exercise in this lab needs to observe a specific HTTP behaviour —
a `429`, a `304`, a paginated `has_more` flag — on demand and every time.
A real public API would make those non-deterministic (today's rate limit
policy is not tomorrow's) and would fail the whole suite the moment the
network is unavailable. `mock_server.py` is under 200 lines of the
standard library's own `http.server`, and every response it sends is
inspectable in that one file.

## The habits this lab is actually teaching, framed as controls

- **A client that cannot stop retrying is a denial-of-service tool aimed
  at someone else's server.** `fetch_with_backoff`'s bounded attempt count
  is not a performance detail; it is the difference between "polite
  client" and "the reason a small open-data portal rate-limits everyone
  after you". Exercise 3 asserts the bound is real by making it fire.
- **A checksum you did not compute is not a checksum.** Exercise 5's
  pinned digest was generated once with `hashlib.sha256` against fixture
  bytes in this repository and is checked, not assumed, every time the
  suite runs.
- **A licence check that returns a bare `True`/`False` throws away the
  information a real project needs.** `check_licence` always returns a
  reason string alongside the boolean, because "allowed, with attribution
  required" and "allowed, no conditions" are both `True` and impose very
  different obligations on whatever you ship.

## If you point this lab's functions at a real API

The client code in `datasource.py` is not toy code — it is the shape a
real client should have. Before pointing it at a real host:

- Real APIs frequently require an `Authorization` header or API key.
  Never hard-code one; read it from an environment variable and keep it
  out of anything you commit.
- Respect the real `Retry-After` value the server sends, rather than
  ignoring it in favour of your own schedule — `fetch_with_backoff`
  already prefers the server's own hint when present.
- A real ETag cache should persist between runs (a small file or SQLite
  table), not live only in a Python dict for the process's lifetime, or
  every fresh run pays full price again.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv
```

Nothing else is created. The harness's final section checks that claim
directly: it looks for any process still listening on a port this lab
opened, for `__pycache__`, for `.pytest_cache`, and fails if it finds one.
