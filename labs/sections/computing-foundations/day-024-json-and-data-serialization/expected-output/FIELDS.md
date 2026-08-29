# Expected output — Day 024 lab

The two `.txt` files in this directory are real captured runs on the
authoring machine (macOS, Apple Silicon, Python 3.14.0, 2026-07-12):

- `json_tools.txt` — a full run of `bash examples/json_tools.sh`.
- `run_tests.txt` — a full run of `bash tests/run_tests.sh` (ends in
  `7 checks, 0 failure(s).`).

## What must be true on every platform

Regardless of OS or Python version, a correct run shows:

1. `examples/samples/config.json` **validates cleanly** (exit 0) and
   pretty-prints with 7 top-level keys.
2. Extracting `coordinates.lat` prints exactly `26.9124`.
3. Extracting `sensors[0]` prints exactly `temperature`.
4. `examples/samples/broken.json` **fails to validate** with a non-zero
   exit status.
5. `bash tests/run_tests.sh` ends with `7 checks, 0 failure(s).` and
   exits 0.

## The one platform-dependent line

The wording of the broken-file error depends on the Python version:

- **Python 3.13 and newer** (as captured here):
  `Illegal trailing comma before end of object: line 4 column 53 (char 97)`
- **Python 3.12 and older**:
  `Expecting property name enclosed in double quotes: line 5 column 1 (char ...)`

Both messages report the same underlying mistake — the trailing comma after
the `sensors` array — and both cause a non-zero exit, which is what the test
checks. The exact character offset is not asserted anywhere.
