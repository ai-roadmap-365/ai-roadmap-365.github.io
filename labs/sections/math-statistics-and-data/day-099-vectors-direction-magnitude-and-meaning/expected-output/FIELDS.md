# What may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 on Apple Silicon (arm64), Python 3.14.0,
NumPy 2.5.2, pytest 9.1.1, bash 3.2.57. Nothing here is typed by hand.

Most of it is arithmetic and will be byte-identical for you. The list below is
everything that is allowed to differ, and why.

## Will be identical

- Every magnitude, distance and dot product printed to 4 decimal places. These
  are IEEE 754 double-precision operations on small integers; any conforming
  platform gives the same answers.
- Every nearest-neighbour answer in `embeddings.txt`, every ranking in
  `norms.txt`, and every `agrees: True` in `byhand.txt`.
- The check count in `test-run.txt`: **87 checks, 0 failure(s)**.
- The test counts: `79 passed` for `tests/`, and `1 passed, 11 skipped` for
  `starter/` before you begin.

## May differ, and the run is still correct

| What | Why | What to do |
| --- | --- | --- |
| The version lines in `test-run.txt` (`python 3.14.0`, `numpy==2.5.2`, `pytest==9.1.1`) | You may have installed different versions | The pin checks in section 1 will fail if you did not install from `requirements/requirements.txt`. That failure is telling you the truth; either install the pins or accept that your numbers are from a different build |
| The pytest timing line (`79 passed in 0.07s`) | Machine speed | Ignore it. Nothing in this lab asserts on a duration |
| `torch is absent` / `jax is absent` / `pandas is absent` | If you happen to have those installed system-wide, and you run the suite against that interpreter rather than a clean `.venv` | Those three checks exist to keep the lesson honest: it describes PyTorch, JAX and pandas from their documentation and reproduces no output from any of them. If you have them, the check will fail and you may ignore it — but the lesson still shows no output from them |

## The one line that is genuinely machine-dependent

In `normalise.txt`:

```
exactly 1.0 : 4 of 7
isclose 1.0 : 7 of 7
```

The second line must be `7 of 7` everywhere: every vector normalises to
magnitude 1 within `rel_tol=1e-9, abs_tol=1e-12`, and that is the claim the
lab makes.

The first line is the interesting one. Four of these seven vectors happened to
normalise to a magnitude that is *exactly* the float `1.0` on this machine, and
three did not — `[1, 1]`, `[0.1, 0.2, 0.3]` and `[2, 3, 6]` each came out at
`0.9999999999999999`. Which vectors land on the nose depends on the order the
operations are performed and on the compiler's floating-point code generation,
so a different build could plausibly split them differently.

What must not change is that **the count is less than 7**. If it ever reads
`exactly 1.0 : 7 of 7`, the `==` trap did not reproduce on that machine and the
lesson's argument would need re-checking there rather than being repeated on
faith. `tests/run_tests.sh` asserts exactly that — the check reads "at least
one normalised vector is NOT exactly 1.0" and fails loudly if it stops being
true. The reference suite carries the same guard as
`test_comparing_a_normalised_norm_with_exact_equality_really_does_fail`.

`[2, 3, 6]` is the sharpest case in the table: its magnitude is exactly `7.0`,
a whole number with an exact binary representation, and dividing by it *still*
does not give back exactly 1.0.

## Files

| File | Produced by |
| --- | --- |
| `byhand.txt` | `python3 byhand.py`, run from `examples/` |
| `agreement.txt` | `python3 agreement.py`, run from `examples/` |
| `normalise.txt` | `python3 normalise.py`, run from `examples/` |
| `norms.txt` | `python3 norms.py`, run from `examples/` |
| `embeddings.txt` | `python3 embeddings.py`, run from `examples/` |
| `starter-progress.txt` | `python3 starter/vectors.py`, run from the lab directory, before any exercise is done |
| `test-run.txt` | `bash tests/run_tests.sh`, run from the lab directory |
