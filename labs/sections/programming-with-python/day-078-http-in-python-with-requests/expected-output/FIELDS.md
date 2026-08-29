# Expected output — Day 078 lab

Real captured runs from the authoring machine (macOS 26.5.1, Apple Silicon,
Python 3.14.0, requests 2.34.2, pytest 9.1.1, httpx 0.28.1, bash 3.2.57,
2026-07-19). Every byte below came out of a command that really ran, against
a server this lab started on 127.0.0.1. **No capture in this directory
involved the internet.**

## Files

- `sample-run.txt` — `raw_socket_demo.py`, `demo.py`, `stdlib_demo.py` and
  `httpx_demo.py`, each run end to end.
- `pytest-runs.txt` — the example suite five ways: whole, fake-session only,
  with timings, with every non-loopback socket blocked, and the starter.
- `test-run.txt` — a full run of `bash tests/run_tests.sh`.

## What is deterministic and what is not

| Varies | Where | Why |
| --- | --- | --- |
| The port, e.g. `127.0.0.1:54037` | every capture | The lab binds port `0`, so the operating system picks a free port each run. That is deliberate: a hard-coded 8000 would collide with whatever you already have running. |
| The `Date:` response header | `raw_socket_demo.py` section 2 | HTTP servers stamp the current time. |
| Elapsed times, e.g. `0.0012s` | `demo.py` sections 1 and 6, pytest durations | Wall-clock measurements on a loopback socket. The magnitudes are the point, not the digits. |
| The sha256 of the streamed body's *prefix* | never | It is fixed: the body is a repeated constant line. |

Everything else — every status code, every byte count, every chunk count,
every connection count, every assertion — is identical on every run and on
every machine, because the server is a fixture rather than a service.

## Required behaviour — the local test server

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /api/readings` | 200 | JSON: `count` 6, all stations |
| `GET /api/readings?station=ALPHA` | 200 | JSON: `count` 4 |
| `GET /api/readings?station=NOWHERE` | 404 | JSON body with `detail: no station named NOWHERE` |
| `GET /api/search?...` | 200 | echoes `raw_query` and the server's parse of it |
| `GET /api/missing` | 404 | `detail: no such station` |
| `GET /api/broken` | 500 | `detail: the server fell over` |
| `GET /old/readings` | 301 | `Location: /api/readings` |
| `GET /api/flaky` | 429 then 200 | `Retry-After: 1`; arm it with `/control/reset?fail=N` |
| `GET /api/slow?seconds=3` | 200 after 3 s | exists so a timeout can really fire |
| `GET /api/large?kb=512` | 200 | exactly `512 * 1024` = 524288 bytes |
| `POST /api/echo` | 201 | echoes method, Content-Type, User-Agent, body size, parsed JSON |
| `GET /control/stats` | 200 | `connections`, `requests`, `flaky_calls` |

`GET /api/large?kb=8` returns exactly 8192 bytes — the body is a 1023-byte
line plus a newline, repeated `kb` times, so every byte count is derivable.

## Required behaviour — the client

| Call | Result |
| --- | --- |
| `fetch_readings(base, "ALPHA", session=s)` | 4 `Reading` objects; `readings[0] == Reading("ALPHA", 0, 12.0)` |
| `summarise(...)` of those | `{"count": 4.0, "min": 12.0, "max": 22.0, "mean": 17.0}` — check by hand: (12+14+20+22)/4 = 17 |
| `fetch_readings(base, "NOWHERE", session=s)` | raises `StationNotFound`, message contains `NOWHERE`, no traceback text |
| `describe_failure(404 response)` | `HTTP 404 (your request was rejected) — no such station` |
| `describe_failure(500 response)` | `HTTP 500 (the server failed) — the server fell over` |
| `session.get(slow, timeout=(3.05, 0.4))` | raises `requests.exceptions.ReadTimeout` in about 0.40 s, not 3 s |
| `backoff_delays(6, jitter=lambda: 1.0)` | `[0.5, 1.0, 2.0, 4.0, 8.0]` |
| `backoff_delays(4, jitter=lambda: 0.0)` | `[0.25, 0.5, 1.0]` |
| `backoff_delays(0)` | raises `ValueError` |
| `get_with_retry(flaky, attempts=4)` after `reset?fail=2` | 200 on attempt **3**; two waits requested; `Retry-After: 1` overrides both |
| `get_with_retry(flaky, attempts=3)` after `reset?fail=99` | raises `ReadingsUnavailable` containing `after 3 attempts` |
| `get_with_retry(missing, attempts=4)` | returns the 404 immediately; zero waits |
| `stream_to_file(large?kb=512, chunk_size=8192)` | `(524288, 64, <64-hex-char digest>)` |
| `make_session()` with no `READINGS_TOKEN` | sends no `Authorization` header |
| `make_session()` with `READINGS_TOKEN` set | sends `Authorization: Bearer …` |

## Required behaviour — the numbers the lesson quotes

| Claim | Where it is proved |
| --- | --- |
| 5 requests through one `Session` open **1** TCP connection | `demo.py` section 7; `test_one_session_reuses_one_connection_for_many_requests` |
| 5 calls to `requests.get` open **5** | the same two places |
| `params=` sends `station=ALPHA+ONE%26station%3DBRAVO` | `demo.py` section 2; `test_params_are_encoded_not_concatenated` |
| An f-string sends `station=ALPHA%20ONE&station=BRAVO`, and the server parses **two** values | the same two places |
| `httpx.Client()` has a default timeout of `Timeout(timeout=5.0)`; `requests` has none | `httpx_demo.py` section 2 |
| `urllib.request` *raises* on a 404 where `requests` returns a response | `stdlib_demo.py` section 2 |

## Test counts

| Command | Result |
| --- | --- |
| `pytest examples -q` | `48 passed`, exit 0, about 1.4 s |
| `pytest examples/test_without_a_server.py -q` | `20 passed`, exit 0, about 0.04 s |
| `PYTHONPATH=tests pytest examples -q` | `48 passed` with every non-loopback socket blocked |
| `pytest starter -q` (exercises unfinished) | `2 passed, 13 skipped`, exit 0 |
| `bash tests/run_tests.sh` | `58 checks, 0 failure(s).`, exit 0 |

Roughly a second of the example suite's 1.4 s is two tests that deliberately
wait 0.4 s each for a timeout to fire. Everything else is in the noise.

## The offline guarantee

`tests/sitecustomize.py` replaces `socket.socket.connect`,
`socket.socket.connect_ex` and `socket.getaddrinfo` so that any attempt to
resolve a hostname or reach an address that is not the loopback interface
raises `NetworkBlocked`. `tests/run_tests.sh` runs the entire example suite
with that file on `PYTHONPATH`, and separately proves the guard is not
vacuous by confirming that a request to a public site under the same guard
fails. Both checks are in section 5 of `test-run.txt`.

## Platform notes

- **macOS and Linux** — identical. `python3`, `bash` and `mktemp -d` behave
  the same, and `http.server` is the same code on both.
- **Windows** — use WSL and follow the Linux path. Several headings contain
  an em dash, so a UTF-8 terminal is needed for them to render; the status
  codes, byte counts and exit codes are unaffected.
- **Python version** — verified on 3.14.0. Python 3.10 or newer is required
  for the `X | None` annotation style used throughout.
- **httpx** — `examples/httpx_demo.py` ran here against httpx 0.28.1, which
  is installed on the authoring machine but is **not** a dependency of this
  lab. On a machine without it the demo prints a short explanation and exits
  0, and the test suite accepts that outcome.
