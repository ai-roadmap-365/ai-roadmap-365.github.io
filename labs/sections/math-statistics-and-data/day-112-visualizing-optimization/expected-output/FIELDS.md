# About these captures

Every file in this directory is the literal stdout of a real run on the
authoring machine (macOS, arm64, Python 3.14.0, numpy 2.5.2, Pillow 12.3.0,
pytest 9.1.1), captured on the date recorded in `metadata.yml`.

## What may legitimately differ on another machine

- **PNG and GIF byte sizes are not checked anywhere in this lab**, precisely
  because they vary across Pillow versions, zlib/libgif builds, and
  platforms even when the pixels are identical. Every test and every
  harness check instead asserts image **dimensions** (`Image.size`),
  **frame counts** (`Image.n_frames`), and **specific pixel values** at
  specific, analytically-known coordinates (the minimum of a bowl, a
  corner of a small grid) — properties a different Pillow build cannot
  legitimately change.
- Floating-point values printed to many significant figures (the learning-
  rate sweep table, the loss-curve numbers) may differ in their last one or
  two digits on a different CPU or numpy build. Every corresponding test
  compares with an explicit tolerance rather than exact equality, except
  where the arithmetic is provably exact (see below).
- `platform.platform()` in section 1 of `test-run.txt` names this machine
  specifically and will differ everywhere else. It is printed for the
  record, not compared against anything.

## What is exact, and provably so, not merely "usually so"

- The well-conditioned bowl (`a = b = 1`) makes the gradient-descent update
  an exact linear recursion, `x_{k+1} = (1 - 2 * lr) * x_k`. Its loss
  sequence is therefore geometric to machine precision on every platform
  with IEEE-754 double-precision floats — which is effectively every
  platform this lab will run on — and `test_log_axis_points_are_collinear`
  asserts a residual under `1e-6` (pixel units), not "close by eye". The
  actual measured residual on this run was on the order of `1e-13`.
- The 3-4-5 triangle path in `starter/test_starter.py`
  (`test_8_path_length_of_a_known_path`) has length exactly 7; this is
  Euclidean geometry, not a measurement, and the test uses `pytest.approx`
  only to absorb ordinary floating-point summation, not because the answer
  is in doubt.

## Files

| File | What it captures |
| --- | --- |
| `01-grid-and-ascii.txt` through `06-two-runs-same-loss.txt` | stdout of each numbered example script, run individually from `examples/` |
| `reference-tests.txt` | `pytest examples -q` |
| `starter-progress.txt` | `pytest starter -q` on an untouched checkout (13 skipped, 0 failed) |
| `test-run.txt` | The full `tests/run_tests.sh` harness output and its exit code |
