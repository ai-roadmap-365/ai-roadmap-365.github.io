# Troubleshooting — Day 079 lab

## `ModuleNotFoundError: No module named 'bs4'`

The distribution is called `beautifulsoup4`; the module it installs is called
`bs4`. You install one name and import the other. If `pip install
beautifulsoup4` succeeded and `import bs4` still fails, you installed into a
different interpreter than the one running your code. Check both:

```bash
.venv/bin/pip show beautifulsoup4 | head -3
.venv/bin/python3 -c "import bs4, sys; print(bs4.__version__, sys.executable)"
```

Use `.venv/bin/python3` and `.venv/bin/pip` explicitly, as every command in
this lab does, and the mismatch cannot happen.

## `ModuleNotFoundError: No module named 'catalogue_scraper'`

The example scripts import each other by module name, so Python needs
`examples/` on its import path:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/demo.py catalogue.csv
```

`tests/run_tests.sh` and `tests/test_scraper.py` set this up for you; only the
direct script invocations need the prefix.

## `pytest: command not found`

`tests/run_tests.sh` looks for pytest in three places, in order: the `PYTEST`
environment variable, this lab's `.venv/bin/pytest`, then your `PATH`. Create
the venv:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the harness at a pytest you already have:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness deliberately fails loudly rather than skipping quietly. A test
suite that silently does nothing is worse than one that refuses to start.

## `NotImplementedError: Exercise 3: select_one, check for None, ...`

That is the lab working. `starter/catalogue_scraper.py` ships with six
exercises unwritten, and the message names the one you have reached. Run the
suite against your own module to see how many are left:

```bash
SCRAPER_MODULE=starter .venv/bin/pytest tests -q
```

You should start at `32 failed, 1 passed` and finish at `34 passed`.

## `requests.exceptions.ConnectionError` or a proxy error on 127.0.0.1

If your machine sets `HTTP_PROXY`, `HTTPS_PROXY` or `ALL_PROXY`, `requests`
honours them — and may try to route even loopback traffic through a proxy that
is not there. Tell it not to:

```bash
NO_PROXY=127.0.0.1 bash tests/run_tests.sh
```

`NO_PROXY` tells `requests` to connect directly to the addresses listed, and
`127.0.0.1` is the only address this lab ever connects to.

## `OSError: [Errno 48] Address already in use`

This should be impossible here, and if you see it you have edited
`fixture_server.py`. The server binds port `0`, which asks the operating
system for any free port; a hard-coded port such as 8000 is exactly what
produces this error. Restore the line:

```python
httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
```

## The suite hangs, or a stray Python process is left running

`serve_fixtures` is a context manager with a `finally` block that calls
`shutdown()`, `server_close()` and `join()`, so a failing test still stops its
server. If you write your own server outside that context manager and a test
raises, you will leak a listener. Find it with:

```bash
ps aux | grep fixture-server
```

and prefer fixing the missing `with` block over killing processes by hand.

## The tests pass but `examples/demo.py` prints a different port each time

That is correct. The port is assigned at run time. Nothing in the lab prints
it, precisely so that captured output stays stable, and nothing in the lab
depends on its value.

## `AttributeError: 'NoneType' object has no attribute 'get_text'`

You chained a method onto a `select_one` that found nothing — the single most
common scraping bug, and the whole subject of Exercise 3. `select_one` returns
`None` when there is no match; check for it before touching the result. The
fixture's `NAV-003` row has no price cell at all, specifically so this
happens to you here rather than at 3 a.m. on someone else's site.

## `ValueError: could not convert string to float: ''`

The same bug wearing a different hat: you got past the `None` check but then
called `float()` on an empty string. Treat "cell absent" and "cell empty" the
same way — both mean "no price", and both should produce `None`.

## The starter suite fails on an import error rather than a NotImplementedError

You have introduced a syntax error or removed an import from
`starter/catalogue_scraper.py`. Run it directly to see the real message:

```bash
.venv/bin/python3 -c "import sys; sys.path.insert(0, 'starter'); import catalogue_scraper"
```

## Windows

Everything here assumes a POSIX shell. Run the lab inside WSL. `bash
tests/run_tests.sh` needs bash; PowerShell will not run it. Outside WSL the
venv paths become `.venv\Scripts\python` and `.venv\Scripts\pip`.
