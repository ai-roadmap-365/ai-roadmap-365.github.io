# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16, offline, with numpy 2.5.2 and pytest 9.1.1 on
CPython 3.14.0. If your run differs in one of the ways listed here, nothing is
wrong. If it differs in any other way, something is.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| Elapsed times, such as `41 passed in 0.06s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing. Nothing in this lab asserts on a duration, deliberately: a test that asserts milliseconds is flaky on a slower machine. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. Nothing in the lab code is version-specific beyond numpy, which is why numpy is the one pinned dependency whose version the harness checks. |
| The pass/skip glyph line, such as `.ssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 32 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| Every number, shape and tuple | all five `0*-*.txt` files | They are computed from twelve small integers with no randomness, no clock and no file system involved. A different number means different arithmetic. |
| `41 passed` | `reference-tests.txt` | The reference suite has forty-one tests. A different count means tests failed to collect. |
| `41 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## The one thing that changes with the numpy version

NumPy 2.0 changed how a single array element prints on its own: `np.int64(36)`
rather than the bare `36` that NumPy 1.x produced. The scripts in `examples/`
avoid that entirely by converting arrays with `.tolist()` before printing, so
the captured output shows plain Python numbers whichever version you have.

Only NumPy 2.5.2 was run here. Nothing in this directory was captured on any
other version, and no claim is made about what NumPy 1.x would print, because
that was not tested. Section 1 of the harness compares the installed version
against `requirements/requirements.txt` and reports a mismatch rather than
letting you discover it later as a mysterious difference.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples && ../.venv/bin/python3 01_matrix_from_scratch.py; cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`matrix.py` and `dataset.py` from beside themselves.
