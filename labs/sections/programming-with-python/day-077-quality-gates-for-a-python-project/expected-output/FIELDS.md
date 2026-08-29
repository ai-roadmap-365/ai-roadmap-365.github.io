# Expected output — Day 077 lab

Every file in this directory is a real capture from the authoring machine
(macOS 26.5.1, Apple Silicon, Python 3.14.0, bash 3.2.57, 2026-07-19) with
ruff 0.15.22, mypy 2.3.0, pytest 9.1.1, coverage 7.15.2 and pytest-cov 7.1.0.
Absolute paths appear as `<repo>`; on your machine they are your real
repository path.

Nothing in this lab reads the clock, the network, or a random number, so the
numbers below are the same on any machine running the pinned tool versions.

## Files

- `gate-pass.txt` — `bash check.sh` on the clean reference project, in both
  modes: the default report-everything run and the `--fail-fast` run. Both are
  green, so both look identical here; the difference only shows when something
  breaks, and `gate-failures.txt` shows that.
- `gate-failures.txt` — the important one. Five fresh copies of the reference
  project, one defect each, one red stage each. This is the evidence that the
  gate is wired in rather than decorative.
- `coverage-reports.txt` — how to read a coverage report, in five parts:
  the two-command form (`coverage run` then `coverage report`), the
  `pytest --cov` one-command form, the 100%-coverage-of-a-buggy-module
  demonstration, the same tests with one assertion added, and the realistic
  assertion-free run against `pricekit` itself.
- `starter-progress.txt` — the starter gate before exercise 1 (no stages, so
  it says yes to everything) and the coverage figure the starter begins with.
- `test-run.txt` — a full run of `bash tests/run_tests.sh`: 39 checks, 0
  failures, exit 0.

## Required behaviour of the reference gate

| Command, run in `examples/` | Result |
| --- | --- |
| `bash check.sh` | five `PASS:` lines, `gate PASSED`, exit 0 |
| `bash check.sh --fail-fast` | identical on clean code, exit 0 |
| `coverage report` | `TOTAL 66 0 26 0 100%` |
| the gate with a formatting defect | `FAIL: format` only, exit 1 |
| the gate with an unused import | `FAIL: lint` only, reporting `F401` and `I001`, exit 1 |
| the gate with `__str__` annotated `-> int` | `FAIL: types` only, reporting `[override]` and `[return-value]`, exit 1 |
| the gate with `+ 1` added to `Money.__add__` | `FAIL: tests` only, 4 failed / 38 passed, exit 1 |
| the gate with an untested function appended to `receipt.py` | `FAIL: coverage` only, `total of 88 is less than fail-under=95`, exit 1 |
| `bash check.sh --fail-fast` with a formatting defect | stops after the format stage; the later stage headers never print |

Each defect trips exactly one stage. That is not a coincidence — it is what a
well-separated gate looks like, and it is why a red build tells you where to
look rather than merely that something is wrong.

## Required behaviour of the coverage demonstration

| Command, run in `examples/coverage-demo/` | Result |
| --- | --- |
| `grep -cE '^[[:space:]]*assert ' test_promo_no_assertions.py` | `0` |
| `coverage run --branch --source=promo -m pytest test_promo_no_assertions.py -q` then `coverage report --show-missing --fail-under=0` | `promo.py 4 0 2 0 100%` |
| `pytest test_promo_with_assertions.py -q` | one failure, `assert 100 == 900`, exit 1 |

The module under measurement is genuinely wrong: `promo_price(1000, True)`
returns 100 where 900 is intended. Coverage reports 100% anyway, because
coverage measures which lines ran, never whether anything about the result was
checked.

## Required behaviour of the starter

| Command, run in `starter/` | Result |
| --- | --- |
| `bash check.sh` as shipped | `gate PASSED (with no stages)`, exit 0 |
| `ruff format --check .` after exercise 1b | flags `tests/test_money.py` only |
| `coverage report` against `fail_under = 95` | `TOTAL 66 27 26 0 55%`, exit 2 |

The starter begins at 55% because it ships tests for `pricekit/money.py` and
none for `pricekit/receipt.py`. Exercise 5 is not a formality: you have to
write real tests to clear the floor.

## Platform notes

- **Linux** is identical apart from the `platform darwin` string that
  pytest-cov prints in its header, which reads `platform linux` there.
- **Windows**: run everything inside WSL. `check.sh` and `run_tests.sh` are
  bash scripts, and the tool paths inside a `.venv` differ on native Windows
  (`.venv\Scripts\` rather than `.venv/bin/`).
- **Different tool versions** will change some text. Ruff's message layout,
  mypy's wording, and pytest's failure formatting all evolve between releases.
  The exit codes and the stage that fails will not change; that is exactly why
  `tests/run_tests.sh` asserts on `FAIL: <stage>` and on exit codes rather
  than on the tools' prose.
- The test runner makes its own temporary directories with `mktemp -d` and
  removes each one as that check finishes, so a completed run leaves nothing
  behind.
