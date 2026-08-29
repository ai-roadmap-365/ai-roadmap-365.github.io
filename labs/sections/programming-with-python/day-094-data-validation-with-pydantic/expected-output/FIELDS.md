# What in this directory is fixed, and what may legitimately differ

Everything here was captured from a real run on 2026-08-16 with Python 3.14.0,
pydantic 2.13.4, pydantic-core 2.46.4 and pytest 9.1.1 on macOS (arm64). If a
line below does not match on your machine, check this file before assuming
something is wrong.

## Files

| File | Produced by |
| --- | --- |
| `coercion.txt` | `python3 examples/coercion.py` |
| `scratch-demo.txt` | `python3 examples/scratch_demo.py` |
| `serialize.txt` | `python3 examples/serialize.py` |
| `gate.txt` | `python3 examples/gate.py` |
| `accepted.jsonl` | `examples/gate.py`, copied out of `out/` |
| `rejects.json` | `examples/gate.py`, copied out of `out/` |
| `byhand.txt` | `python3 starter/byhand.py` |
| `pytest-tests.txt` | `pytest tests -q` |
| `pytest-starter.txt` | `pytest starter -q` |
| `run_tests.txt` | `bash tests/run_tests.sh` |

## Fixed — these should match exactly

- Every count: 12 records seen, 4 accepted, 8 rejected by the gate; 9 accepted
  and 3 rejected by the from-scratch validator; 5 accepted and 7 rejected by
  the pydantic schema alone (the gate drops one more for the duplicate id, a
  batch rule no per-record schema can see).
- Every error `type` and every `loc`. These are the parts of a
  `ValidationError` that pydantic treats as an interface, and every assertion
  in this lab is written against them.
- `47 passed` from `pytest tests`, `1 passed, 9 skipped` from `pytest starter`,
  and `62 checks, 0 failure(s).` from `tests/run_tests.sh`.
- The coercion table in `coercion.txt`. Every cell is the result of an actual
  `TypeAdapter(...).validate_python(...)` call, so the table is a statement
  about this version of pydantic and nothing else.

## May legitimately differ

- **Timings.** `pytest` prints a wall-clock duration (`in 0.34s`). Nothing
  asserts on it.
- **Temporary paths.** `run_tests.txt` line 41 has been sanitised to
  `<tmpdir>/day094-gate.XXXXXX/`; a real run prints your platform's temporary
  directory there. `tests/run_tests.sh` runs the gate into a temporary
  directory so the lab stays clean, whereas `gate.txt` was captured from the
  default run, which writes to `out/` and says so.
- **Version banner.** Section 1 of `run_tests.txt` prints the interpreter and
  package versions it found. If yours differ from the pins in
  `requirements/requirements.txt`, that section will report a failure — which
  is the point of it.
- **`error_type` names across pydantic versions.** These are stable within a
  major version but are not promised forever. One was checked here and is worth
  recording: a model-wide `frozen=True` reports `frozen_instance`, not the
  per-field `frozen_field`. Observed in 2.13.4, asserted as observed.
- **Error `msg` text.** Present in `rejects.json` because a human reads the
  report. Nothing in this lab asserts on it, and it is the field most likely to
  be reworded by a future release.

## What is invented

All station codes, site names, operator initials and measurements in
`data/raw-readings.json` and in the test fixtures are invented for this lab.
There is no real monitoring network, no real person and no real measurement
anywhere in this directory. The operator initials in particular are made up
precisely so that nothing here resembles a record about a living individual.
