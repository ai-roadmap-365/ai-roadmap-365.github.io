# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16, offline, with numpy 2.5.2 and pytest 9.1.1 on
CPython 3.14.0, macOS 26.5.2 (Apple Silicon, arm64). If your run differs in one
of the ways listed here, nothing is wrong. If it differs in any other way,
something is.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| Elapsed times, such as `76 passed in 0.34s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing. Nothing in this lab asserts on a duration, deliberately: a test that asserts milliseconds is flaky on a slower machine. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The exact text of NumPy's `ValueError` for mismatched shapes | `03-from-scratch-vs-numpy.txt` | The captured message names `matmul` and quotes a gufunc signature. NumPy has reworded this message across versions. The *type* is what the tests assert; the wording is quoted only to show you what you will actually see. |
| The pass/skip glyph line, such as `.ssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 51 skipped`. As you complete exercises, passes replace skips, up to `52 passed`. That is the file changing because you changed, not because anything broke. |

## Will differ if your NumPy version differs

| What | Where | Why |
| --- | --- | --- |
| Every measured number in the dimensionality tables | `07-curse-of-dimensionality.txt`, and the `curse_values` check in `test-run.txt` section 5 | They come from `numpy.random.default_rng(103)`. NumPy guarantees the same stream for the same seed within a major version, and does not promise it across one. On a different NumPy the digits move. |

What must **not** change even then is the shape of the result: mean absolute
cosine falling at every step up in dimension, tracking the exact formula
`gamma(d/2) / (sqrt(pi) gamma((d+1)/2))` to within a few percent, and the
nearest-to-furthest distance ratio collapsing towards 1. The reference suite
asserts that shape rather than the digits, for exactly this reason. Section 5
of the harness does check four literal values, because on the pinned version
they are fixed and a silent change of generator would otherwise go unnoticed.

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| Every similarity, distance, angle, dot product and ranking over the six articles | `01-*.txt` through `06-*.txt` | They are computed from twenty-four small integers with no randomness, no clock and no file system involved. A different number means different arithmetic. |
| `9.0554`, `8.0623`, `1.0000000000` | `01-the-length-confound.txt` | The three numbers the whole day rests on: the distance to the doubled copy, the distance to a genuinely different article, and the cosine similarity that ignores both. |
| `0.585786` against `1.000000` | `05-not-a-metric.txt` | The triangle-inequality failure. Exact: `2 - sqrt(2)` against `1`. |
| `roast-chicken 0.993884` and `race-day-nutrition 0.903482` | `06-semantic-search.txt` | The two asserted search results. |
| The three floating-point values `0.9999999999999998`, `1.0` and `1.0000000000000002` | `03-from-scratch-vs-numpy.txt` | These are IEEE 754 double arithmetic on small integers, and are the same on any conforming platform. If yours differ, your floating point is not IEEE 754 doubles, which is worth knowing. |
| `76 passed` | `reference-tests.txt` | The reference suite has seventy-six tests. A different count means tests failed to collect. |
| `49 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## Why section 6 of `test-run.txt` looks strange

It re-runs the whole harness with one expectation deliberately swapped for a
wrong one, and asserts that the re-run fails. The captured file therefore
contains a passing suite that proves it is capable of failing. That is
intentional: a green test suite proves nothing until you have watched it go
red.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples
../.venv/bin/python3 01_the_length_confound.py
../.venv/bin/python3 02_dot_product_and_sign.py
../.venv/bin/python3 03_from_scratch_vs_numpy.py
../.venv/bin/python3 04_same_ranking_on_the_sphere.py
../.venv/bin/python3 05_not_a_metric.py
../.venv/bin/python3 06_semantic_search.py
../.venv/bin/python3 07_curse_of_dimensionality.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`similarity.py` and `catalogue.py` from beside themselves.
