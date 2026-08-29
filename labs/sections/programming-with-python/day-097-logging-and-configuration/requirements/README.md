# Dependencies

**None.** This lab installs nothing, and `requirements.txt` is deliberately
empty of packages. That is not minimalism for its own sake: the argument of
the day is that the standard library already contains a complete logging
framework and everything you need to resolve configuration, and you cannot
judge `structlog` or `pydantic-settings` fairly until you have built the small
version yourself.

| Tool | Version used here | Where it comes from | Licence |
| --- | --- | --- | --- |
| `python3` | 3.14.0 | Whatever Python you installed on Day 43 | PSF licence |
| `bash` | 3.2.57 | Preinstalled on macOS and every Linux distribution | GPL |

Modules used, all from the standard library: `logging`, `logging.config`,
`logging.handlers`, `json`, `os`, `sys`, `tomllib`, `argparse`, `pathlib`,
`dataclasses`, `random`, `tempfile`, `shutil`, `time`, `io`, `importlib.util`,
`subprocess`, `re`.

Check what you have:

```bash
python3 --version
python3 -c "import tomllib, logging.config, logging.handlers; print('ready')"
```

## Minimum version, and why

**Python 3.11 or newer**, for `tomllib`. That is the only floor this lab has,
and it is a real one: `tomllib` was added in 3.11 (2022), and the configuration
half reads its file layer with it.

If you are on 3.10 or older, `pip install tomli` gives you the same parser
under the name `tomli` — `tomllib` was adopted from it, so the code is the
same. Everything else here has been in the standard library far longer:
`logging` and `logging.config` since Python 2.3 (2003), `dictConfig` since
Python 2.7 and 3.2 (2010), `argparse` since 3.2.

The `str | Path` type hints and the `dict[str, Any]` builtin generics also
want 3.10 or newer, and `from __future__ import annotations` at the top of
each file keeps them from being evaluated at import time.

## If your Python is somewhere unusual

Both scripts take an override rather than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
PYTHON=/path/to/python3 bash starter/03_check.sh
```

They fail loudly with that instruction if they cannot find one, rather than
quietly skipping the checks that need it.

## What is deliberately absent

**No `structlog`, no `loguru`, no `python-json-logger`.** All three are good,
all three are free, and all three are covered in the lesson's Alternatives
section from their documentation. None of them is installed on the machine
this lab was captured on, so **no output is reproduced for any of them** — the
lesson says so plainly where it discusses each one. The JSON formatter you
build in exercise 5 is about forty lines and is what `python-json-logger`
does; writing it once is how you find out that a formatter is a class with one
method.

**No `pydantic-settings`, no `dynaconf`.** Same treatment: described, not
demonstrated, because neither is installed here. Day 94 covered pydantic
itself, and `pydantic-settings` is the natural next step for a real service —
after you have written the resolver by hand and know what it is doing for you.

**`python-dotenv` is the one exception**, and it is worth being precise about
why. It is not used by this lab and is not needed by it. It does, however,
happen to be present in the system interpreter this lab was captured on, at
version 1.2.2 — pulled in as a dependency of something else installed on that
machine. Because it was genuinely available, the lesson runs it once and shows
the real output, clearly marked as an aside. You do not need it to complete
anything here, and nothing in the lab imports it.

**No log-shipping platform.** The lesson names the category and stops there.
Which collector or hosted service you use is an operations decision with
prices attached, it changes yearly, and none of it changes the four objects
inside your process. What travels is the JSON line, and you have written the
thing that produces it.
