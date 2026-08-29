# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-17, with numpy 2.5.2 and pytest 9.1.1 on CPython 3.14.0,
macOS 26.5.2 on Apple Silicon (arm64). If your run differs in one of the ways
listed here, nothing is wrong. If it differs in any other way, something is.

This lab measures speed, and that makes this file more important than usual.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| **Every millisecond and microsecond figure** | `03-same-answer-faster.txt` sections 1 and 2, `07-nan-and-when-not-to-vectorise.txt` section 4, `test-run.txt` section 5 | Wall-clock timing on one machine on one day. Your processor, your load, your Python build. Nothing in this lab asserts a duration. |
| **Every speedup ratio** | the same places | The authoring machine measured 106x to 134x across the three operations. The tests assert only that the ratio is above 20, which is a claim about the shape of the gap rather than about this hardware. If yours is 40x, the lesson still holds. |
| Elapsed times, such as `107 passed in 0.73s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Same reason. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `03-same-answer-faster.txt` section 1, `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The pass/skip glyph line, such as `.sssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 70 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| `36,000,056` and `8,000,000` bytes | `01-list-versus-array.txt` section 3, `test-run.txt` section 5 | Computed from `sys.getsizeof`, and on CPython 3.14 an `int` is 28 bytes and a list is 56 bytes of header plus 8 per pointer. A different total means a different Python build, and the accompanying ratio of 4.5 would move with it. |
| `-128`, and `[-16, -6, -2]` | `02-dtypes-and-overflow.txt` sections 3 and 4 | Two's complement arithmetic in eight bits. Not a NumPy choice and not machine-dependent. |
| `warnings raised      none` | `02-dtypes-and-overflow.txt` section 3 | Measured on numpy 2.5.2. A reference test asserts the ABSENCE of the warning, so if a future NumPy started emitting one the suite would report it rather than let this page go quietly stale. |
| `elementwise identical ... : True`, three times | `03-same-answer-faster.txt` section 2 | The whole claim of the day. The loop and the vectorised expression perform the identical IEEE-754 operations on the identical bits. |
| The twenty readings, and every count and selection taken from them | `05-masks-and-selection.txt` throughout | `numpy.random.default_rng(104)` is a specified algorithm producing a specified stream. A reference test compares the generator against the twenty values written out in `dataset.py`, so a change would be reported rather than absorbed. |
| `[3, 2, 0]` and the three article names | `06-axes-views-and-ranking.txt` section 6, `test-run.txt` section 5 | Cosine similarities of six hand-written integer vectors. Re-derivable with a pen. |
| `999` and `8` | `06-axes-views-and-ranking.txt` section 3 | Writing through a view changes the original; writing through a copy does not. |
| `1390` | `07-nan-and-when-not-to-vectorise.txt` section 7 | See the note below. This one is genuinely platform-dependent in principle, and is discussed rather than asserted as a fixed count. |
| `2.3333333333333335` and `7.0` | `07-nan-and-when-not-to-vectorise.txt` section 3 | 7/3 and 1+2+4, in float64. |
| `80 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| `107 passed` | `reference-tests.txt` | The reference suite has 107 tests. A different count means tests failed to collect. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## The number that looks like a bug and is not

**`x ** 0.5` disagreeing with `np.sqrt` on 1,390 of a million values.**

This is real, it was measured, and it is the most interesting thing in the lab.

IEEE-754 requires the square-root operation to be *correctly rounded*: there is
exactly one right answer for every input, and the hardware instruction produces
it. Both `math.sqrt` and `numpy.sqrt` use that instruction, which is why they
agree on all one million values here — zero disagreements, asserted by a test.

`x ** 0.5` calls a general power routine instead. `pow` has no
correctly-rounded requirement, because computing an arbitrary power exactly is
much harder than computing a square root, so its implementation is allowed to be
off by a unit in the last place. Here it is off on about one value in seven
hundred, always by that one unit — the first disagreement in the captured file
is `0.808767639263571` against `0.8087676392635711`.

**The count of 1,390 depends on the maths library your Python was built
against**, so it may differ on your machine, and the reference test asserts only
that the count is greater than zero and smaller than one percent, and that the
largest disagreement is under `1e-15`. What must not change is the direction:
`math.sqrt` agrees exactly and `x ** 0.5` does not.

It matters here because the lesson's central claim is that a vectorised
expression is *the same computation* as the loop. That is true of the operation,
not of anything that would give the same answer in exact arithmetic. If a
vectorised rewrite of yours suddenly needs a tolerance it did not need before,
this is the first thing to check.

## The two comparisons the lab deliberately does NOT make with a tolerance

`03-same-answer-faster.txt` compares a million loop results against a million
array results with `==`. That is unusual advice for floating point and it is
correct here: `2.5`, `1.25`, `0.25` and `0.75` are all exactly representable in
binary, each element goes through the same operations in the same order, and
there is no room for a difference to appear. Using a tolerance would hide the
very fact being demonstrated.

The one place a tolerance IS used is `dataset.TOL`, `1e-12`, and it appears only
where two genuinely different routes to the same number are compared — the
vectorised cosine similarities against Day 103's row-at-a-time version, which
sum in a different order.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples && ../.venv/bin/python3 01_list_versus_array.py; cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`vectorize.py` and `dataset.py` from beside themselves.
