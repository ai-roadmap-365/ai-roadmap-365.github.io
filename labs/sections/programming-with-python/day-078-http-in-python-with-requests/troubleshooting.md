# Troubleshooting — Day 078 lab

Every symptom below was produced on the authoring machine at least once while
building this lab. The fixes are the real ones.

## Installation and tooling

**`ModuleNotFoundError: No module named 'requests'`**
The interpreter running your script is not the one `requests` is installed in.
This is the single most common problem in the whole lab. Check which is which:

```bash
which python3
.venv/bin/python3 -c "import requests, sys; print(requests.__version__, sys.executable)"
```

Run the demos with the virtual environment's interpreter —
`.venv/bin/python3 examples/demo.py` — or activate the environment first.
`tests/run_tests.sh` sidesteps this by resolving `python3` from the same
directory as the `pytest` it found.

**`FAIL: pytest not found.`**
The runner looked in `$PYTEST`, then `.venv/bin/`, then `PATH`, and found
nothing. Create the environment as the README says, or run
`PYTEST=/path/to/pytest bash tests/run_tests.sh`. It fails loudly on purpose:
a test suite that skips itself when the tool is missing is worse than one that
stops.

**`ModuleNotFoundError: No module named 'demo_server'`**
pytest was pointed at a file outside the directory that holds the modules, or
you ran a starter test without `starter/conftest.py` present. Run
`pytest starter` or `pytest examples` from the lab directory, not from
somewhere else with a full path to one file.

## The server

**`OSError: [Errno 48] Address already in use`**
This should be impossible here, because the lab binds port `0` and lets the
operating system choose. If you see it, you have edited a port number into
`demo_server.py`. Put the `0` back. That is the whole reason it is there.

**The tests hang for five seconds and then say the server never became ready.**
`wait_until_accepting` polls the port and gives up after five seconds. Either
the server thread crashed at start-up (run `python3 examples/demo_server.py`
on its own and read the traceback) or something on your machine is blocking
loopback connections — some endpoint-security products do this. Try
`python3 -c "import socket; socket.create_connection(('127.0.0.1', 22), 1)"`
and see whether loopback works at all.

**A stray Python process is left running after a failed test.**
It should not be: `running_server` is a context manager, the thread is a
daemon thread, and `shutdown()` and `server_close()` run in a `finally`. If
you have interrupted a run with Ctrl-C mid-start, check with
`ps aux | grep demo_server` and stop it. Then read `running_server` and note
that the cleanup is in `finally` for exactly this reason.

## requests

**A call never returns and the program appears frozen.**
You forgot `timeout=`. `requests` has no default timeout, so a connection to
a host that accepts and then says nothing will wait for as long as your
operating system's TCP keepalive allows — often hours. Every request in this
lab passes `timeout=(3.05, 10.0)`. Make that a habit today and you will never
debug this again.

**`requests.exceptions.ConnectTimeout` when you expected `ReadTimeout`.**
The tuple is `(connect, read)`, in that order. `timeout=(0.4, 3.05)` gives up
on the handshake; `timeout=(3.05, 0.4)` gives up on the body. Against the
loopback interface the connection is instant, so the first value can be almost
anything and the second is the one that fires.

**`requests.exceptions.MissingSchema: Invalid URL 'api/readings'`**
You dropped the `http://` prefix, usually by building the URL from a base that
was empty. Print the URL before you send it.

**`.json()` raises `requests.exceptions.JSONDecodeError`.**
The body was not JSON. This almost always means the status code was not what
you assumed: an HTML error page from a proxy, or an empty 204. Check
`response.status_code` and `response.headers["Content-Type"]` *before* calling
`.json()`, which is exactly what `describe_failure` does.

**`raise_for_status()` did not raise on a 3xx.**
It raises for 4xx and 5xx only, and by the time you see the response
`requests` has already followed the redirect. Use `allow_redirects=False` if
you want to see the 301 itself.

**Your query string arrived wrong.**
Print `response.request.path_url` — it shows exactly what went down the wire.
If you see `station=ALPHA%20ONE&station=BRAVO` where you meant one value, you
concatenated instead of using `params=`. The `/api/search` endpoint exists to
show you the server's side of the same story.

## The retry exercise

**`ReadingsUnavailable: gave up after 4 attempts` when you expected success.**
The flaky endpoint was still armed from a previous test. Call
`/control/reset?fail=N` before each retry test — the reference tests do.

**The retry test takes six seconds.**
You used the real `time.sleep` instead of passing a recorder in. The `sleep`
parameter exists so the schedule can be asserted without waiting; see
`RecordingSleep` in `examples/demo.py`.

**Your backoff numbers do not match.**
`backoff_delays` returns the waits *between* attempts, so there are
`attempts - 1` of them, and each is multiplied by `0.5 + 0.5 * jitter()`.
With `jitter=lambda: 1.0` the multiplier is 1.0 and you get the raw schedule;
with `lambda: 0.0` you get half of it. If your first value is 1.0 rather than
0.5, you started the exponent at 1 instead of 0.

## The streaming exercise

**The chunk count is 1, not 64.**
You called `response.content` (or `.text`, or `.json()`) somewhere before
iterating. Any of those reads the whole body immediately and defeats
`stream=True`.

**The file is empty.**
`iter_content` yields nothing after the response has been consumed or closed.
Keep the `with session.get(...)` block open around the whole loop.

## The connection-reuse exercise

**Five requests still show five connections.**
You used `requests.get(...)` inside the loop instead of `session.get(...)`.
The module-level functions create and discard a `Session` per call, which is
the whole point of the comparison.

**The count is one higher than you expected.**
The server counts every accepted connection from the moment it started,
including the readiness probe. Take a `before` reading and subtract, as the
tests and `demo.py` do.

## The offline guard

**`NetworkBlocked: blocked a name lookup for '...'`**
Something in the code you just added tried to reach a real host while
`tests/sitecustomize.py` was loaded. That is the guard doing its job. Remove
the call; this lab is offline by design.
