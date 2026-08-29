# Day 078 lab — Talk to a Server You Control

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** HTTP in Python with requests
- **Day number:** 78 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-078-http-in-python-with-requests
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-078-http-in-python-with-requests` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 78 is the day your program stops being alone on your machine. Every lab
before this one read a file, computed something, and printed it. This one asks
another process for data over a network protocol, and everything that makes
distributed systems hard shows up at once: a call that might never return, a
server that says no, a server that says "not now, try again in a second", a
response too large to hold in memory, and a status code that means failure
arriving inside a request that succeeded perfectly.

You will build a client against a server you control. `examples/demo_server.py`
is about two hundred lines of standard library — `http.server`, `socket`,
`threading` — bound to `127.0.0.1` on a port the operating system picks at run
time. It can produce every case that matters on demand: a 200 with JSON, a
404, a 500, a 301 redirect, a 429 carrying `Retry-After`, an endpoint that
takes three seconds so a timeout can really fire, and a 512 KiB body so
streaming is not a hypothetical.

**Nothing in this lab touches the internet after the one-time install.** That
is not a convenience; it is the design. A lab that hit a real public API would
be slow, would be flaky, would break the day that API changed, would fail for
you on a plane, and would quietly teach you to hammer somebody else's server.
And it is not merely promised: `tests/sitecustomize.py` blocks every
non-loopback socket, `tests/run_tests.sh` runs the whole example suite under
that guard, and one further check proves the guard is not vacuous by
confirming a request to a public site is refused under it.

The last exercise is the one that pays off. Because every function in
`client.py` takes `session` as a parameter — Day 74's boundary argument
applied to the network — the whole client can be tested with a forty-line fake
and **no server at all**. The test suite proves that by copying three files to
an empty temporary directory, deliberately leaving `demo_server.py` behind,
and running the fake-session suite there.

## Learning objectives

- Read an HTTP request and response as the bytes they actually are, using a
  plain socket and no library.
- Send a GET with a query string using `params=`, and explain what an f-string
  would have done to a value containing a space and an ampersand.
- Tell `.text`, `.content` and `.json()` apart, and know when each is wrong.
- Treat a 404 and a 500 as data rather than as crashes, and turn either into
  one sentence a human can act on.
- Set a timeout on every request, and watch one fire against an endpoint that
  deliberately takes three seconds.
- Implement retry with exponential backoff and jitter, honour `Retry-After`,
  and say precisely which status codes deserve a retry and which never do.
- Use a `Session` for shared headers and connection reuse, and prove the reuse
  by reading the server's own count of accepted TCP connections.
- Stream a large body to disk a chunk at a time instead of loading it.
- Read a credential from the environment and never from a source file.
- Test a networked function with an injected fake session, with no server, no
  socket and no patching.

## Prerequisites

- Day 74: boundaries, test doubles, and the argument that you inject a
  boundary rather than patch it. This lab is that argument made concrete.
- Day 71 to 73: pytest, fixtures, `pytest.raises`, parametrization.
- Day 66: exception hierarchies — `ReadingsError` and its two subclasses.
- Day 69: dataclasses and type hints.
- Day 65: reading and writing JSON.
- Day 43: creating a virtual environment with `python3 -m venv`.
- Days 1 to 40 gave you the network layers this lab sits on top of: an address,
  a port, a TCP connection, and a protocol carried over it.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, requests 2.34.2, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.10+ and bash).
- **Windows** — use WSL and follow the Linux path. Several headings contain an
  em dash, so a UTF-8 terminal is needed for them to render; the status codes,
  byte counts, exit codes and assertions are unaffected.

## Hardware requirements

Any computer that runs Python 3. The largest thing the lab moves is a 512 KiB
response, and it moves it in 8 KiB chunks. The test suite finishes in a few
seconds, of which most is two tests waiting 0.4 seconds each for a timeout to
fire on purpose. No GPU, no special memory, and no internet access at test
time.

## Required software

- `python3` (3.10 or newer; tested on 3.14.0).
- `requests` 2.34.2 and `pytest` 9.1.1 — installed below.
- `bash` for the test runner (preinstalled on macOS and Linux).
- The server needs nothing installed: `http.server`, `socket`, `threading`,
  `json` and `urllib.parse` all ship with Python.

## Free and open-source options

Everything here is free and open source: Python, bash, the standard library,
requests (Apache 2.0) and pytest (MIT). See
[`requirements/README.md`](requirements/README.md) for the per-package detail.
No account, no API key, no purchase.

The lesson's Alternatives section compares four libraries. Two —
`urllib.request` and `http.client` — need no installation at all, and
`examples/stdlib_demo.py` runs them here so you can see exactly what
`requests` is saving you. The fourth, `httpx`, is deliberately not a
dependency: `examples/httpx_demo.py` runs the comparison if httpx happens to
be installed and prints a short explanation if it is not.

## Installation

```bash
cd labs/sections/programming-with-python/day-078-http-in-python-with-requests
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/python3 -c "import requests; print(requests.__version__)"
```

Those last two should print `pytest 9.1.1` and `2.34.2`. `.venv/` is ignored by
version control — never commit it. If you already have both packages
elsewhere, skip the virtual environment and run the suite as
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## File structure

```text
day-078-http-in-python-with-requests/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── examples/
│   ├── demo_server.py                 ← the server you control: stdlib only, 127.0.0.1, ephemeral port
│   ├── client.py                      ← the reference client: timeouts, retries, streaming, injected session
│   ├── fake_session.py                ← a scripted stand-in for requests.Session — the Day 74 payoff
│   ├── raw_socket_demo.py             ← HTTP as bytes, with no HTTP library at all
│   ├── demo.py                        ← the whole story in one run, eight sections
│   ├── stdlib_demo.py                 ← the same calls in urllib.request and http.client
│   ├── httpx_demo.py                  ← the same calls in httpx, if you have it
│   ├── conftest.py                    ← one local server for the whole test session
│   ├── test_client.py                 ← 28 tests against the local server
│   └── test_without_a_server.py       ← 20 tests against a fake session, no server anywhere
├── starter/
│   ├── client.py                      ← YOUR working file (exercises 1-6)
│   ├── test_client.py                 ← YOUR working file (exercise 7)
│   ├── conftest.py                    ← provided complete: the server fixture
│   └── NOTES.md                       ← YOUR written answers (exercise 8)
├── tests/
│   ├── run_tests.sh                   ← 58 checks; exits 0 only if all pass
│   └── sitecustomize.py               ← the offline guard: blocks every non-loopback socket
├── expected-output/
│   ├── sample-run.txt                 ← real captured runs of all four demos
│   ├── pytest-runs.txt                ← real captured runs of the suites, five ways
│   ├── test-run.txt                   ← real captured run of the test suite
│   └── FIELDS.md                      ← required behaviour, and what varies between runs
├── requirements/
│   ├── requirements.txt               ← requests==2.34.2, pytest==9.1.1
│   └── README.md                      ← what each dependency is for, and what is stdlib
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, with the virtual environment installed.

```bash
# 1. HTTP with no HTTP library: type a request by hand, read the raw response.
.venv/bin/python3 examples/raw_socket_demo.py

# 2. The whole lab in one run: eight sections, one local server.
.venv/bin/python3 examples/demo.py

# 3. The same work in the standard library — nothing installed, nothing needed.
.venv/bin/python3 examples/stdlib_demo.py

# 4. And in httpx, if it happens to be installed. Exits 0 either way.
.venv/bin/python3 examples/httpx_demo.py

# 5. The reference suite: 28 tests against the local server, 20 against a fake.
.venv/bin/pytest examples -q

# 6. The 20 that need no server at all. Read the file; it is the point of the day.
.venv/bin/pytest examples/test_without_a_server.py -q

# 7. Prove the whole suite is offline: every non-loopback socket blocked.
PYTHONPATH=tests .venv/bin/pytest examples -q

# 8. Your task: exercises 1-6 in starter/client.py, 7 in starter/test_client.py,
#    8 in starter/NOTES.md. Unfinished exercises are skipped, so this is green
#    from the first minute.
.venv/bin/pytest starter -q

# 9. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `examples/raw_socket_demo.py` — opens a plain TCP socket to the local test
  server, sends a request line, three headers and a blank line typed out by
  hand, and prints both directions byte for byte. Read this before anything
  else. After it, `requests` stops being magic and becomes a convenience over
  text you have already seen.
- `examples/demo.py` — eight sections. (1) the pieces of a request and a
  response, including `.content` versus `.text` versus `.json()`. (2) `params=`
  against an f-string, with a value containing a space and an ampersand — the
  f-string smuggles in a second query parameter and the server proves it.
  (3) a 404 as a successful response, and the three ways to handle it.
  (4) a redirect followed and unfollowed. (5) a read timeout of 0.5 s firing
  against a 3 s endpoint. (6) retry with backoff against a 429, with the sleep
  injected so it takes milliseconds. (7) five requests through a `Session`
  opening one TCP connection where five bare calls open five. (8) 512 KiB
  streamed in 64 chunks.
- `examples/stdlib_demo.py` — the same four calls in `urllib.request` and
  `http.client`, so the comparison in the lesson is something you have watched
  rather than read. Note especially that `urllib.request` *raises* on a 404
  where `requests` returns a response.
- `examples/httpx_demo.py` — the modern alternative, including the difference
  that matters most: `httpx.Client()` has a default timeout of 5 seconds and
  `requests` has none.
- `pytest examples -q` — 48 tests. 28 open a real socket to the local test
  server; 20 open nothing at all.
- `PYTHONPATH=tests pytest examples -q` — the same 48, with
  `socket.connect` and `socket.getaddrinfo` replaced so that any attempt to
  reach a non-loopback address raises. Still 48 passed.
- `bash tests/run_tests.sh` — 58 checks while the starter is unfinished, 53
  once you complete every exercise. Exits 0 only if all of them pass.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) and
[`expected-output/pytest-runs.txt`](expected-output/pytest-runs.txt) — real
captured sessions. The heart of it:

```text
$ python3 examples/raw_socket_demo.py

  bytes sent (147 bytes)
  ----------------------
    GET /api/readings?station=ALPHA HTTP/1.1\r\n
    Host: 127.0.0.1:54037\r\n
    User-Agent: day078-raw-socket/1.0\r\n
    Accept: application/json\r\n
    Connection: close\r\n
    \r\n          <- the blank line: headers finished
```

```text
$ python3 examples/demo.py

2. params= versus gluing strings together
=========================================
  station value    : 'ALPHA ONE&station=BRAVO'
  params=          : /api/search?station=ALPHA+ONE%26station%3DBRAVO
    server parsed  : {'station': ['ALPHA ONE&station=BRAVO']}
  f-string         : /api/search?station=ALPHA%20ONE&station=BRAVO
    server parsed  : {'station': ['ALPHA ONE', 'BRAVO']}
  the f-string smuggled a second parameter in. params= encoded it.

7. Session and connection reuse
===============================
  5 calls, one Session      : 1 TCP connection(s)
  5 calls, requests.get()   : 5 TCP connection(s)
```

Only the port number, the `Date` header and the elapsed times vary between
runs, and all three are explained in
[`expected-output/FIELDS.md`](expected-output/FIELDS.md), which also lists the
exact required behaviour of every endpoint and every client function.

## Validation steps

1. `python3 examples/raw_socket_demo.py` exits 0 and shows a request that
   starts `GET /api/readings?station=ALPHA HTTP/1.1` and a response that starts
   `HTTP/1.1 200 OK`.
2. `python3 examples/demo.py` section 2 shows `station=ALPHA+ONE%26station%3DBRAVO`
   for `params=` and two parsed values for the f-string.
3. Section 5 of the same run raises `ReadTimeout` in about 0.50 s against an
   endpoint that would have taken 3 s.
4. Section 7 shows `1 TCP connection(s)` for the Session and `5` without one.
   If yours shows 5 and 5, you used `requests.get` inside the loop.
5. Section 8 shows `524288` bytes read as `64` chunks of at most 8192.
6. `pytest examples -q` reports `48 passed` in under two seconds.
7. `pytest examples/test_without_a_server.py -q` reports `20 passed` in about
   0.04 s — no server was started for any of them.
8. `PYTHONPATH=tests pytest examples -q` still reports `48 passed`. Then prove
   the guard is not vacuous:
   `PYTHONPATH=tests .venv/bin/python3 -c "import requests; requests.get('https://example.com', timeout=2)"`
   must fail with `NetworkBlocked`.
9. Every exercise in `starter/client.py` is complete, `pytest starter -q`
   reports no skips, and `starter/NOTES.md` is filled in with your own numbers
   and sentences rather than blanks.
10. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `58 checks, 0 failure(s).`
Once every exercise is complete, eight structural checks are replaced by three
behavioural ones and the line becomes `53 checks, 0 failure(s).` The command
exits 0 on success and non-zero on any failure, so it is usable in continuous
integration. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

Three of the checks are worth reading the runner for:

- **the offline proof.** The whole example suite is re-run with
  `tests/sitecustomize.py` on `PYTHONPATH`, which replaces `socket.connect`,
  `socket.connect_ex` and `socket.getaddrinfo` so any non-loopback address
  raises. A separate check then confirms a request to a public site under the
  same guard *is* refused, so the guard cannot be silently doing nothing.
- **the no-server proof.** Three files — `client.py`, `fake_session.py` and
  `test_without_a_server.py` — are copied to an empty temporary directory,
  deliberately without `demo_server.py` or `conftest.py`, and pytest is run
  there. Twenty tests pass. That is only possible because the boundary is a
  parameter.
- **the signature check.** `inspect.signature` confirms that
  `fetch_readings`, `get_with_retry` and `stream_to_file` all take a
  keyword-only `session`, and that `get_with_retry` takes an injectable
  `sleep` and `jitter`. If a future edit hard-codes `requests.get`, this fails.

## Cleanup

The lab writes nothing into your working directory. The streamed file goes
into pytest's `tmp_path` or a `tempfile.TemporaryDirectory`, and the server is
shut down in a `finally` block by a context manager. The runner passes
`-p no:cacheprovider`, so pytest leaves no cache directory behind.

```bash
rm -rf .venv                 # remove the virtual environment when you are done
git checkout -- starter/     # optional: reset your work
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list. The five you
are most likely to meet: `ModuleNotFoundError: No module named 'requests'`,
which always means the interpreter running your script is not the one the
package is installed in; a call that never returns, which always means a
missing `timeout=`; `ConnectTimeout` where you expected `ReadTimeout`, because
the tuple is `(connect, read)` in that order; a streaming loop that reports one
chunk instead of 64, because something read `.content` before the loop; and
`ReadingsUnavailable: gave up after 4 attempts` in the retry exercise, which
means the flaky endpoint was still armed from an earlier test and needs
`/control/reset`.

## Security notes

See [security.md](security.md). Short version: the server binds `127.0.0.1`
and not `0.0.0.0`, which is the difference between a private fixture and a
service open to everyone on the coffee-shop Wi-Fi. No credential appears in
any file; `make_session` reads `READINGS_TOKEN` from the environment and the
one test that needs it sets a fake value through `monkeypatch` for the
duration of that test. This lab uses plain HTTP only because it talks to
itself over loopback — anything leaving your machine must use HTTPS, and
`requests` verifies certificates by default for a reason. And the day's own
security point: a retry loop with no backoff, no jitter and no attempt cap is
a small denial-of-service tool pointed at whoever you are calling.

## Extension exercises

1. **Add a 503 with a `Retry-After` date.** `Retry-After` may legally be a
   number of seconds *or* an HTTP date. Add an endpoint that sends the date
   form, then make `get_with_retry` handle both. Note that the reference
   implementation currently ignores what it cannot parse as a float, and
   decide whether that is a reasonable default or a bug.
2. **Measure what a connection actually costs.** Time 50 requests through one
   `Session` and 50 through `requests.get`, and record both. Then read the
   lesson's note about TLS and predict how the gap would change over HTTPS.
3. **Make the timeout fire on connect instead of read.** Point the client at
   an address that will not answer — a port on `127.0.0.1` with nothing
   listening is the safe way — and catch `ConnectionError`. Then find an
   address that accepts and never replies, and produce a `ConnectTimeout`.
   Write down which exception you got for which cause.
4. **Add a paginated endpoint** that returns 50 readings at a time with a
   `next` link, and write a client function that follows it to exhaustion.
   Cap the number of pages, and say in a comment what happens without the cap
   if the server has a bug that always returns the same `next`.
5. **Break the boundary and watch the suite notice.** Change
   `fetch_readings` to call `requests.get` directly instead of using the
   `session` parameter, then run `bash tests/run_tests.sh`. Both the
   signature check and the no-server suite fail. Put it back, and write one
   sentence explaining what the failure told you.
6. **Write the client you will need in Course 07.** Sketch a `complete(prompt)`
   method against a model API: a `Session` with an `Authorization` header from
   the environment, a timeout, retry on 429 and 5xx with backoff and jitter,
   and a streaming mode that yields tokens as they arrive. Test all of it with
   a `FakeSession` and no model. You now have the skeleton of every model
   client in the rest of the course.

## Navigation

- **Previous day:** Day 77 — Quality Gates for a Python Project
  (`labs/sections/programming-with-python/day-077-quality-gates-for-a-python-project/`).
- **Next day:** Day 79 — Web Scraping Responsibly
  (`labs/sections/programming-with-python/day-079-web-scraping-responsibly/`).
- **Week 12 project:** the Personal Automation Toolkit
  (`labs/sections/programming-with-python/projects/week-12/`), which needs a
  client that sets timeouts, retries the right statuses, and can be tested
  without a network.
