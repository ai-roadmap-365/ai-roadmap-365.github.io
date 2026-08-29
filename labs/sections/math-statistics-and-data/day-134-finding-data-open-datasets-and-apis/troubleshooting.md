# Troubleshooting

## `pytest: command not found`, or the harness exits before any check

You have not created the lab's virtual environment, or you are calling
bare `pytest` rather than the one in `.venv`.

```bash
cd labs/sections/math-statistics-and-data/day-134-finding-data-open-datasets-and-apis
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

The harness looks for `.venv/bin/pytest` first, then anything on your
PATH. To point it at an interpreter of your own:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'datasource'` or `'mock_server'`

You ran pytest from the wrong directory, or named the file instead of the
directory. Run from the lab directory and name the directory:

```bash
.venv/bin/pytest starter          # correct
.venv/bin/pytest starter/test_datasource.py   # also fine
cd starter && ../.venv/bin/pytest .           # also fine
```

## `import file mismatch` and a collection error

You ran `pytest examples starter` in one command. `starter/test_datasource.py`
and `examples/test_datasource.py` share a module name, and pytest collects
test modules by dotted name, so the second import collides with the
first. Run them as two commands:

```bash
.venv/bin/pytest starter -q
.venv/bin/pytest examples -q
```

The harness runs the combined form deliberately and asserts it fails, so
this is documented behaviour, not a surprise.

## A test hangs, or times out waiting for the server

Every server-using test takes the `mock_api` or `stubborn_mock_api`
fixture, which starts a real `ThreadingHTTPServer` in a background thread.
If a test hangs, the most common cause is a firewall or security tool
intercepting loopback traffic on some machines — try running once with
that tool paused, or confirm `127.0.0.1` connections are not blocked.
`fetch_raw` sets a 5-second `timeout`, so a genuinely broken server fails
loudly with a `URLError` rather than hanging forever.

## Exercise 3 fails with a different attempt count than expected

`mock_api` and `stubborn_mock_api` each carry their **own** rejection
counter, reset per test by the fixture. If your test reuses one server for
more than one call to `/ratelimited`, the counter keeps climbing across
calls within the same test — read `conftest.py` to see that each fixture
starts a fresh server, and call each server's `/ratelimited` path only
once per assertion block if you want the counts in `00_brief.md` to match
exactly.

## Exercise 4's byte counts are not what you expected

`bytes_over_wire` is `len(body)` of the raw HTTP response, not the size of
the object you get back. A `200` response returns the real payload's
length; a `304` response has an empty body by construction, so this is
`0` regardless of how large the cached copy is. If you are seeing a
non-zero count on the second call, you likely built a fresh `cache` dict
for the second call instead of reusing the one from the first.

## `RateLimitExceeded` was not raised when you expected it

Check which fixture you used. `mock_api` relents after 2 rejections, so
any `max_attempts >= 3` will succeed against it. Only `stubborn_mock_api`
(relents after 10) will exhaust a small `max_attempts` budget and raise.

## `version mismatch` in section 1 of the harness

The harness compares every installed version against
`requirements/requirements.txt`. Nothing in this lab depends on a
pandas-3.0-specific or pytest-9-specific behaviour, so an older pandas 2.x
or pytest 7.x will almost certainly still pass every exercise; the version
check is there to flag drift, not to gate correctness.

## The lab left something behind

It should not, and the harness's final section checks. If you find a
stray directory:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

## Windows

Use WSL2 and follow the Linux instructions. Native Windows works for the
Python parts if you substitute `.venv\Scripts\python.exe` and
`.venv\Scripts\pytest.exe`, but `tests/run_tests.sh` is a bash script and
needs Git Bash or WSL; it will not run in `cmd.exe` or PowerShell.
