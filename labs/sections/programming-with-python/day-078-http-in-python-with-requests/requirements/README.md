# Dependencies — Day 078 lab

**Two third-party packages. The server you talk to is not one of them — it is
built entirely from the standard library.**

## The pinned list

`requirements.txt` contains exactly two lines:

```
requests==2.34.2
pytest==9.1.1
```

| Dependency | Version | Licence | Why this lab needs it |
| --- | --- | --- | --- |
| requests | 2.34.2 | Apache License 2.0 (declared in the project's own metadata) | The subject of the day. The lab uses `Session`, `params=`, `timeout=`, `.json()`, `raise_for_status()`, `stream=True` with `iter_content`, `allow_redirects=False`, and the `requests.exceptions` hierarchy. |
| pytest | 9.1.1 | MIT (the `License-Expression` field of the installed distribution's own metadata) | The test runner from Day 71. This lab needs `pytest.raises`, `@pytest.mark.parametrize`, `tmp_path`, `monkeypatch`, session-scoped fixtures, and its exit code. |

Both are free and open source. Neither has a paid tier, an account, or
telemetry. Both versions were installed and verified on the authoring machine
on 2026-07-19.

## What is NOT in the list, and why that matters

**The server.** `examples/demo_server.py` is a subclass of
`http.server.BaseHTTPRequestHandler` served by `ThreadingHTTPServer`, with
`socket`, `threading`, `json` and `urllib.parse` doing the rest. All standard
library. You already have it. That is not a shortcut — it is the point:
Python ships with a working HTTP server, which is why "start a server you
control and test against that" costs you nothing.

**The alternatives the lesson compares.** `urllib.request` and `http.client`
are standard library too, which is why `examples/stdlib_demo.py` runs on a
machine with nothing installed at all. Run it and see:

```bash
python3 examples/stdlib_demo.py
```

**httpx.** `examples/httpx_demo.py` is the fourth alternative, and httpx is
deliberately *not* pinned here. If it happens to be installed, the demo runs
and prints the comparison; if it is not, the demo says so and exits 0. It ran
on the authoring machine against httpx 0.28.1. Install it yourself if you want
to compare:

```bash
.venv/bin/pip install httpx
```

## Install once

From this lab's directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/python3 -c "import requests; print(requests.__version__)"
```

Those last two commands should print `pytest 9.1.1` and `2.34.2`. You created
your first virtual environment on Day 43; this is the same procedure.
`.venv/` is ignored by version control — never commit it.

## The network, precisely

The install needs the network **once**, to download two packages from the
Python Package Index. That is the only moment any part of this lab reaches
beyond your own machine.

After that, **nothing in this lab touches the internet** — not the demos, not
the example suites, not `tests/run_tests.sh`. Every socket opened goes to
`127.0.0.1`, the loopback interface, on a port the operating system assigned
at run time. This is not a promise; the test suite proves it. Section 5 of
`tests/run_tests.sh` runs the entire example suite with `tests/sitecustomize.py`
loaded, which replaces `socket.connect` and `socket.getaddrinfo` so that any
attempt to resolve a hostname or reach a non-loopback address raises
immediately — and then proves the guard is not vacuous by confirming that a
request to a public site under the same guard is refused.

If you already have both packages somewhere else, skip the virtual
environment and point the suite at that pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The runner resolves `python3` from the same directory as the pytest it found,
so the demos import the same `requests` the tests do.

## Check your Python

```bash
python3 --version
```

Verified on 3.14.0. Python 3.10 or newer is required, because the code uses
the `X | None` annotation syntax throughout.
