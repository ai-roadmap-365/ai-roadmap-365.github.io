# Dependencies

Three packages, all free and open source, all pinned to an exact version.

| Package | Version | Why this lab needs it | Licence |
| --- | --- | --- | --- |
| `requests` | 2.34.2 | The HTTP client the toolkit's fetch adapter uses (Day 78). Everything it does here could be done with the standard library's `urllib.request`; `requests` is used because sessions, timeouts and JSON decoding are one line each, and because it is what you will meet in other people's code | Apache-2.0 |
| `pytest` | 9.1.1 | Runs the property suite in `tests/test_toolkit.py` (Days 71–73) | MIT |
| `setuptools` | 83.0.0 | The build backend named in `examples/pyproject.toml`. It is what turns `pip install -e examples` into two working console scripts (Day 83). Python's `venv` no longer installs it by default, so it has to be asked for | MIT |

Install them:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## What is deliberately absent

**No scheduling library.** cron, launchd and systemd timers are already on your
machine, and a Python process that sleeps in a loop to schedule itself is a
process that has to be kept alive, monitored and restarted — which is the job
you just gave yourself instead of the one the operating system already does.
Day 81 argued this at length; the schedule files under `examples/schedule/` are
the result.

**No configuration library.** `tomllib` has been in the standard library since
Python 3.11, and the four-layer precedence in `config.py` is thirty lines. A
dependency for that is a dependency you will still be maintaining in a year.

**No logging library.** `logging` is in the standard library, the JSON
formatter is fifteen lines, and the redaction filter is the part that actually
matters and would have needed writing regardless.

**No retry library.** The bounded retry with exponential backoff is twelve
lines in `adapters.py`. Reach for a library when you need jitter, circuit
breaking, or per-exception policies — not before.

## The network

The install above is the only step that needs the internet. **The tests
themselves need no network at all**: they start a fixture server on 127.0.0.1
on a port the operating system chooses, and nothing in this lab ever resolves a
name or opens a socket to anywhere else.
