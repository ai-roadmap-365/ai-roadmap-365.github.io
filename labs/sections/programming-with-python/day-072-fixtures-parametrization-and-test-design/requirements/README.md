# Dependencies — Day 072 lab

**One third-party package. Free and open source. Installed once, then the
whole lab runs offline.**

| Dependency | Pinned version | Why this lab needs it | Licence and cost |
| --- | --- | --- | --- |
| `pytest` | `9.1.1` | Fixtures, parametrization, markers, `--collect-only`, and the built-in `tmp_path`, `capsys` and `monkeypatch` fixtures — the entire subject of the day | MIT licence, free and open source |
| `python3` | 3.8 or newer (tested on 3.14.0) | Runs everything; `dataclasses`, `csv`, `datetime` and `pathlib` are all standard library | Python Software Foundation Licence, free |
| `bash` | any (tested on 3.2.57) | The outer test harness | Free software, preinstalled on macOS and Linux |

Weeks 8 to 10 were standard-library-only on purpose. Week 11 is the first
week that genuinely needs a third-party tool, because the week is *about*
those tools — you cannot learn fixtures from a library that does not have
them. The version above was verified on 2026-07-19 by running
`pytest --version` on the authoring machine.

## The one-time install

You set up virtual environments on Day 43. The same three lines apply here,
run from the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That last command should print `pytest 9.1.1`. The `.venv/` directory is
ignored by version control and is safe to delete and recreate at any time.

**The install is the only step that needs the network.** After it, every
command in this lab runs entirely offline: nothing here opens a socket,
reads the clock, or calls out to a service. If you are working somewhere
without a connection, install once while you have one.

## If you cannot install anything

The test harness will find pytest in three places, in this order: an explicit
`PYTEST=/path/to/pytest` on the command line, this lab's `.venv/bin/pytest`,
and finally whatever `pytest` is on your `PATH`. So if your system already
has a pytest — from a package manager, from a shared environment, from a
previous project — you can point the suite at it:

```bash
PYTEST=/usr/local/bin/pytest bash tests/run_tests.sh
```

A different pytest version will still run this lab. The exact collected
counts the harness asserts (36, 13, 11, 21, 35) depend on the test files, not
on the pytest version, and every flag used here — `--collect-only`, `-q`,
`-k`, `-m`, `-s`, `--strict-markers` — has been in pytest for many years.

## Why pin an exact version

`pytest==9.1.1` rather than `pytest` or `pytest>=9`. A pinned version is the
difference between "the suite passed" and "the suite passed, and I can tell
you exactly what ran". This lab asserts precise numbers of collected items
and precise summary strings; a floating dependency is a slow leak that turns
those assertions into a mystery six months from now. Pin in a lab, pin in a
project, and upgrade deliberately.
