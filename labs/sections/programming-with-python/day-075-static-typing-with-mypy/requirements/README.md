# Dependencies for the Day 075 lab

This lab needs two third-party tools. Both are free and open source, both
install from the Python Package Index with `pip`, and both run entirely on
your machine — nothing here sends code anywhere.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `mypy` | `2.3.0` | The static type checker the whole lesson is about. It reads your annotated source without executing it and reports where a value flows somewhere its annotation does not allow. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. This lab needs it because the entire point is the contrast: a green pytest suite over a module mypy immediately rejects. |

Versions are pinned exactly so that error messages, error codes and exit
statuses match the captured output in `expected-output/`. A newer mypy may
reword a message; the bracketed error codes are far more stable, which is why
the test suite greps for the codes rather than the prose.

## Licences

mypy and pytest are both distributed under the MIT licence, stated on each
project's own documentation site (linked from the lesson's source list). Both
are maintained in the open and cost nothing to use, personally or
commercially.

## One-time install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/mypy --version
.venv/bin/pytest --version
```

Day 43 covered `python3 -m venv` in full; this is the same pattern. The
virtual environment lives in `.venv/` inside the lab, is already excluded
from version control, and can be deleted at any time with `rm -rf .venv`.

## Network

Installing needs the network, once. After that the lab runs completely
offline: mypy analyses local files, pytest runs local tests, and no script
here opens a socket.

## Running without a lab-local environment

If you already have mypy and pytest available — a project virtual environment
you have activated, or a system installation — the test runner will find them
on your `PATH`. You can also point it at specific binaries:

```bash
MYPY=/path/to/mypy PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Cache directories

mypy writes an incremental cache so repeated runs are fast. Run it by hand and
you get a `.mypy_cache/` directory in whatever folder you ran it from; it is
excluded from version control and safe to delete. The test suite avoids the
question entirely by pointing mypy at a temporary cache directory that is
removed when the run finishes, so `bash tests/run_tests.sh` leaves nothing
behind.
