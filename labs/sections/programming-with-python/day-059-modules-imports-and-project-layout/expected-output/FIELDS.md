# Expected output — Day 059 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The package is deterministic:
`top_n` breaks ties alphabetically, so given the same input it prints the same
report and the same numbers on every platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference package driven end to end: run as a program
  with a file argument (`python3 -m wordstats sample.txt`) and with standard
  input, then imported as a library (`from wordstats import tokenize, top_n`)
  and a demonstration that importing the same module twice returns the same
  object (`a is b` is `True`).
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (18 checks, 0 failures). Any absolute path is shown as
  `<repo>`; on your machine it is your real repository path.

## Required behaviour on every platform

Running `python3 -m wordstats sample.txt` from the `examples/` directory (the
bundled `sample.txt` holds "The cat sat on the mat." and two more lines) must
print exactly:

```text
19 words, 10 unique
1. the: 6
2. cat: 2
3. dog: 2
4. on: 2
5. sat: 2
```

Imported as a library, the public API must behave as follows:

| Call | Result |
| --- | --- |
| `wordstats.__version__` | `'1.0.0'` |
| `tokenize('Hello, HELLO world!')` | `['hello', 'hello', 'world']` |
| `count_words(['x', 'y', 'x'])` | `{'x': 2, 'y': 1}` |
| `top_n(['b', 'a', 'b', 'a', 'c'], 2)` | `[('a', 2), ('b', 2)]` (ties alphabetical) |
| `import wordstats.tokens as a; import wordstats.tokens as b; a is b` | `True` (imported once) |
| `from wordstats.__main__ import report` | succeeds without running `main` (the guard) |

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- `python3 -m wordstats` must be run from the directory that *contains* the
  `wordstats/` package (so the package is found on `sys.path`, whose first
  entry for `-m` is the current directory). The `examples/` and `starter/`
  directories each carry their own `sample.txt` for this reason.
- No `__pycache__` directories are left behind: the test runner sets
  `PYTHONDONTWRITEBYTECODE=1` before importing anything.
- Windows: run inside WSL, or substitute `python` for `python3` if that is how
  Python is exposed. The package is pure standard-library Python and behaves
  identically everywhere.
