# Dependencies -- Day 135 lab

**One third-party package. The API you talk to is not one of them -- it is
built entirely from the standard library.**

## The pinned list

`requirements.txt` contains exactly two lines:

```
pandas==3.0.5
pytest==9.1.1
```

| Dependency | Version | Licence | Why this lab needs it |
| --- | --- | --- | --- |
| pandas | 3.0.5 | BSD 3-Clause | `pandas.json_normalize`, `DataFrame.explode`, `pandas.to_numeric`, `pandas.to_datetime`, `pandas.concat` -- everything this lesson's ingestion pipeline flattens, types and assembles with. |
| pytest | 9.1.1 | MIT | The test runner. This lab needs fixtures, `pytest.raises`, `tmp_path`, and skip-on-unfinished markers. |

Both are free and open source. Neither has a paid tier, an account, or
telemetry. Both versions were installed and verified on the authoring
machine on 2026-08-20.

## What is NOT in the list, and why that matters

**The API.** `examples/api_server.py` is a subclass of
`http.server.BaseHTTPRequestHandler` served by `ThreadingHTTPServer`, with
`socket`, `threading` and `json` doing the rest -- standard library. You
already have it.

**The HTTP client.** This lab fetches every page with
`urllib.request.urlopen`, also standard library. No `requests`, no `httpx`.
The lesson names both as leading options and says plainly that neither ran
here: `urllib.request` is the one this lab actually exercises, because a
day about flattening JSON does not need a third-party HTTP client to prove
the flattening.

**pydantic.** The lesson describes schema validation with pydantic from its
documentation. It is not installed in the authoring virtual environment and
no pydantic code was run for this lab; every assertion of shape in this lab
is the `check_contract` function in `examples/ingest.py`, written by hand
against pandas dtypes.

## Install once

From this lab's directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/python3 -c "import pandas; print(pandas.__version__)"
```

Those last two commands should print `pytest 9.1.1` and `3.0.5`.

## The network, precisely

The install needs the network **once**, to download two packages from the
Python Package Index. After that, nothing in this lab touches the internet.
Every socket opened by the tests or the examples goes to `127.0.0.1`, the
loopback interface, on a port the operating system assigned at run time --
never a hard-coded port, and never a real host.

If you already have both packages somewhere else, skip the virtual
environment and point the suite at that pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The runner resolves `python3` from the same directory as the pytest it
found, so the examples import the same pandas the tests do.

## Check your Python

```bash
python3 --version
```

Verified on 3.14.0. Python 3.10 or newer is required, because the code uses
the `X | None` annotation style.
