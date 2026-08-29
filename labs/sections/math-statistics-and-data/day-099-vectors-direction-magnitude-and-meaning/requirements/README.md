# Requirements

Two packages, both pinned to the exact versions this lab was written and run
against.

| Package | Pinned version | Why the lab needs it |
| --- | --- | --- |
| `numpy` | 2.5.2 | The array library everything else in numerical Python imitates. It is used in exactly two places: `examples/agreement.py`, which proves the pure-Python implementation and NumPy give the same answers on the same inputs, and the two test suites, which assert that agreement |
| `pytest` | 9.1.1 | Runs `tests/test_vectors.py` and the `starter/` exercise suite |

Both are free and open source: NumPy is BSD-3-Clause, pytest is MIT.

## The versions are pinned on purpose

`expected-output/` was captured from a run against exactly these versions, and
`tests/run_tests.sh` checks the installed versions against this file. If you
install something else, that check fails — which is the harness telling you the
truth rather than quietly comparing your run against numbers it did not produce.

## Install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

This is the only step that needs a network connection. Everything after it runs
offline.

## What the lab does not need

Nothing else. The nine vector functions the lab asks you to write use
`math.sqrt` from the standard library and nothing more, and `starter/vectors.py`
is checked by the harness for the absence of a NumPy import — writing the loop
yourself is the exercise.

The lesson also discusses PyTorch tensors, JAX arrays and pandas Series. None
of the three is installed here, and the lesson reproduces no output from any of
them; it describes them from their published documentation and says so. The
test harness confirms their absence so that claim cannot rot.
