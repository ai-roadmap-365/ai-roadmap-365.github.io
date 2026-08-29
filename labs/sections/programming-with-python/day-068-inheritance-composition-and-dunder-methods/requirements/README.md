# Requirements

## Software

| Requirement | Version | Why |
| --- | --- | --- |
| `python3` | 3.8 or newer (tested on 3.14.0) | Runs every script in this lab |
| `bash` | any modern version | Runs `tests/run_tests.sh` |

Nothing is installed. There is no `pip install` step, no virtual environment
to create, no `requirements.txt` to resolve, and no account to register.

## Python modules used

All four are part of the standard library and ship with Python itself:

| Module | Used for |
| --- | --- |
| `functools` | `@total_ordering`, which derives `<=`, `>` and `>=` from `__lt__` |
| `abc` | `ABC` and `@abstractmethod` in step 6 |
| `collections.abc` | `Iterable` and `Sized`, to show `isinstance` checking methods rather than ancestry |
| `traceback`, `importlib.util`, `os`, `sys` | Printing a stable short traceback, loading numbered example files by path in the tests, and letting step 5 import the reference `kitchen.py` beside it |

## Why 3.8 or newer

`typing.Protocol` arrived in Python 3.8 (PEP 544), and the lesson's
`Alternatives` section uses it. Everything else in this lab — the data model,
`abc`, `functools.total_ordering`, `collections.abc` — has been available far
longer.

One detail is version-dependent and worth knowing, because the exact text
appears in the expected output. The message for instantiating an incomplete
abstract subclass was reworded between the two versions checked here. On
3.14.0, which produced the captured output, you get:

```text
TypeError: Can't instantiate abstract class PastryStation without an implementation for abstract method 'prepare'
```

On 3.11.14 the same failure reads:

```text
TypeError: Can't instantiate abstract class PastryStation with abstract method prepare
```

Both are the same refusal at the same moment, naming the same class and the
same method; only the sentence changed. The tests match on the class and
method names rather than the full sentence, so they pass on either. If your
Python prints the shorter wording, nothing is wrong.

## Network, credentials, and privileges

- **Network:** not used. Every script runs entirely offline.
- **API keys:** none. Nothing here talks to a service.
- **Privileges:** none. Never run any part of this lab with `sudo`.
- **Files written:** none by the lab itself. The test suite creates one
  temporary directory with `mktemp -d` and removes it via an `EXIT` trap.

## Platform notes

macOS and Linux run every command exactly as written; the lab was authored
and executed on macOS with Apple Silicon.

On Windows, run the lab inside WSL. The Python scripts themselves are fully
portable and will run under native Windows Python unchanged, but
`tests/run_tests.sh` is a bash script and needs a POSIX shell. If you have no
WSL, you can still run each `python3 examples/...` command from PowerShell
and check the output against `expected-output/sample-run.txt` by eye — you
will simply lose the automated suite.

## Determinism

This lab has no timing measurements, no random numbers, no file sizes, and no
network calls. Every figure in `expected-output/` is reproducible byte for
byte on any machine running Python 3.12 or newer. Hash *values* are not
printed anywhere — only hash *equality* is compared — so Python's per-process
string hash randomisation does not affect any output.
