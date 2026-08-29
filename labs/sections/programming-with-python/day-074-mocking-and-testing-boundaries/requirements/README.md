# Dependencies — Day 074 lab

**One third-party package. `unittest.mock` is not one of them — it ships with
Python.**

## The pinned list

`requirements.txt` contains exactly one line:

```
pytest==9.1.1
```

| Dependency | Version | Licence | Why this lab needs it |
| --- | --- | --- | --- |
| pytest | 9.1.1 | MIT (the `License-Expression` field of the installed distribution's own metadata) | The test runner from Day 71. This lab needs its `tmp_path` fixture, `pytest.raises`, `@pytest.mark.parametrize`, and — most of all — its exit code, because four of this lab's checks assert that a test suite **fails**. |

pytest is free and open source. There is no paid tier, no account, and no
telemetry. Version 9.1.1 was verified on the authoring machine on 2026-07-19.

## What is NOT in the list, and why that matters

`unittest.mock` — `Mock`, `MagicMock`, `patch`, `create_autospec`, `call` — is
part of the Python standard library. It has been since Python 3.3, when Michael
Foord's `mock` package was adopted into the standard library through PEP 417.
You already have it. There is nothing to install and nothing to pin.

The same goes for everything else this lab imports: `datetime`, `dataclasses`,
`ast`, `tempfile`, `time` and `random` are all standard library. The
`sensor_service.py` module that stands in for a network service uses `time` and
`random` to be slow and unpredictable — it opens no socket and contacts nothing.

The lesson's Alternatives section covers four optional libraries — `pytest-mock`
(the `mocker` fixture), `responses` and `requests-mock` for HTTP, and
`freezegun` for time. All four are free and open source, all four install with
`pip`, and **none of them is needed for this lab**. That is deliberate: the
argument the lesson makes is that a hand-written fake usually beats all of
them, and a lab that could not be completed without a mocking library would
undercut its own point.

## Install once

From this lab's directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That last command should print `pytest 9.1.1`. You created your first virtual
environment on Day 43; this is the same procedure, one directory along.
`.venv/` is ignored by version control — never commit it.

## Offline after that

The install needs the network once, to download pytest from the Python Package
Index. After that, **nothing in this lab touches the network at any point** —
not the demos, not the example suites, not `tests/run_tests.sh`. The whole
subject of the day is not reaching the outside world during a test, so a lab
that phoned home would be an odd way to teach it.

If you already have pytest 9.1.1 somewhere else, skip the virtual environment
and point the suite at it:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Check your Python first:

```bash
python3 --version
```

Verified on 3.14.0. Python 3.10 or newer is required, because the patch tests
use the parenthesised multi-line `with (...)` form.
