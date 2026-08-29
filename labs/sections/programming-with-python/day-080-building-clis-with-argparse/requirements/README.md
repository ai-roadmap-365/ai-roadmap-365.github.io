# Dependencies — Day 080 lab

**One package, and it is only for the tests.**

The tool you build in this lab has **no third-party dependencies at all**.
`argparse` has been in the Python standard library since Python 3.2, released
in 2011, and so has everything else the tool touches. That is not an accident
of this lab's design — it is one of the strongest practical arguments for
argparse, and it is worth stating plainly rather than burying: a command-line
tool written with argparse can be handed to anyone with a Python interpreter
and it runs. No install step, no version pin, no network.

| Module | Used in | Why |
| --- | --- | --- |
| `argparse` | `notes.py` | the whole command-line interface: parser, subcommands, types, choices, groups, help |
| `json` | `notes.py` | the store format, and the `--format json` output |
| `csv` | `notes.py` | the `--format csv` export, quoted correctly by `csv.writer` |
| `os` | `notes.py` | reading `$NOTES_STORE` for the configuration-precedence rule |
| `sys` | `notes.py` | the three real streams and the process exit code |
| `pathlib` | `notes.py` | reading and writing the store file |
| `datetime` | `notes.py` | the `--on` date, converted by the custom `iso_date` type |
| `dataclasses` | `notes.py` | the small `Streams` record that carries stdin, stdout and stderr |

## What is in requirements.txt, and why

```text
pytest==9.1.1
```

`pytest` is needed only by `tests/test_parser.py`, the in-process half of the
suite — the part that calls `parse_args(["add", "hello"])` directly and
asserts on the resulting namespace without starting a process. You met pytest
on Day 71 and used it for the whole of Week 11.

pytest is free and open source (MIT licence). The exact version above is the
one the captured output in `expected-output/` came from; any recent pytest
will do, and the runner accepts an existing installation.

## Install

```bash
cd labs/sections/programming-with-python/day-080-building-clis-with-argparse
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

`tests/run_tests.sh` looks for pytest in three places, in order: the `PYTEST`
environment variable, this lab's `.venv/bin/`, and then whatever is on your
`PATH`. If it finds none it prints the two commands above and exits non-zero —
it never skips silently, because a suite that quietly does nothing is worse
than a suite that fails.

If you already have pytest somewhere else:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## No network, no account, no key

Nothing in this lab reaches the network at any point, including the install
step if you already have pytest. There is no account to create, no API key,
and nothing to pay for. The alternatives discussed in the lesson — `click`
and `typer` — are also free and open source, and neither is needed here.
