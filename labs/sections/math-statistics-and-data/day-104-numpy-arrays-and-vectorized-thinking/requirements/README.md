# What this lab installs, and what it costs you

Two packages, both free, both open source, no account and no key.

| Package | Version pinned here | Licence | Why it is here |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | The subject of the day. Today it stops being the answer key beside a from-scratch implementation and becomes the thing being taught. |
| `pytest` | 9.1.1 | MIT | Runs both suites: the reference tests in `examples/` and your running score in `starter/`. |

Both versions are pinned exactly. Section 1 of `tests/run_tests.sh` reads the
installed numpy and compares it against this file rather than trusting it, so a
mismatch is reported rather than discovered later as a puzzling number.

## Why a version this specific

Two things in this lab depend on the NumPy major version and are asserted
rather than described:

- **Integer overflow is silent.** On numpy 2.5.2, `np.array([127],
  dtype=np.int8) + np.array([1], dtype=np.int8)` returns `-128` with no
  exception and no warning. A reference test records the absence of the warning
  so that if a future NumPy started emitting one, the suite would say so and the
  lesson could be corrected instead of quietly going stale.
- **A Python scalar does not widen an array.** Since NumPy 2, `np.array([127],
  dtype=np.int8) + 1` stays `int8` and wraps. Under NumPy 1 the promotion rules
  differed. The harness checks the major version is 2 or later for this reason.

## The network

Installing these two packages is the only thing in this lab that touches the
network. Nothing here opens a socket, reads a URL or needs an API key, and
section 7 of the test harness greps every source file in `examples/` and
`starter/` to prove it.

## If you cannot install anything at all

You cannot do most of this lab, and it would be dishonest to pretend otherwise:
NumPy is the subject.

What you can still do on a bare `python3` with only the standard library:

- write `scale_and_offset_loop`, `roots_loop` and `clip_loop`, which use
  nothing but `math`;
- reproduce the memory measurement, which needs only `sys.getsizeof` — the
  helper `list_bytes` in `starter/vectorize.py` runs without NumPy, and the
  28-bytes-per-integer figure is the whole point of it;
- reason through every prediction in `starter/answers.py`, which is where most
  of the thinking is anyway.

What you lose is the entire right-hand column: every vectorised version, the
speed comparison that motivates the day, boolean masking, `argsort`, views
versus copies, and `nan`.

## Disk

Roughly 60 MB for the virtual environment, almost all of it NumPy. `rm -rf
.venv` from the lab directory is a complete undo.
