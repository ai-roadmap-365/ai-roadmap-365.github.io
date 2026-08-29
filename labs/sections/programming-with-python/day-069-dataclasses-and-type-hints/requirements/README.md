# Dependencies — Day 069 lab

**Python 3 only. No third-party packages, no network, no API key.**

- `python3` (**3.10 or newer**; tested on 3.14.0). You set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only: `dataclasses` and `json` in the lab files, plus
  `sys` and `pathlib` so the drivers can import the module sitting beside
  them. There is deliberately no `requirements.txt`.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.10` or higher, you are ready.

## Why 3.10 and not 3.8

The lab files annotate their fields with **builtin generics** such as
`list[str]` rather than `typing.List[str]`, which needs Python 3.9 or newer.
The floor is set one version higher, at 3.10, so that everything the lesson
shows alongside the lab also runs unchanged — the `X | None` spelling for
optional values, and the `slots` and `kw_only` options to `@dataclass`. None
of those three appear in the lab files themselves, but you will want to try
them, and a 3.10 floor means the code you read is the code you would write
today rather than a compatibility variant.

## The optional type checker

One step in this lab — `examples/check_types.sh` — is marked optional
precisely because it needs software this lab does not install. It looks for
`mypy` or `pyright`, and:

- If it finds one, it runs it over `examples/scoring.py` and shows the result.
- **If it finds none, it says so, describes the two planted errors, and exits
  0.** That is the normal path here. No checker is installed in this
  environment, and nothing in the lab or its tests requires one.

If you want to try a checker on your own machine later, both are free and
open source and install with pip:

```bash
python3 -m pip install mypy      # then: python3 -m mypy examples/scoring.py
```

Do that in a virtual environment (Day 43) rather than into your system
Python. It is genuinely optional — the required exercise,
`examples/inspect_runtime.py`, demonstrates the same point from the runtime
side and needs nothing but the standard library.

## Why the standard library is enough

This is the lesson in miniature. `dataclasses` and `typing` are in the box
because defining a record and describing its shape are things every Python
program does. You will meet **pydantic** later, and it is excellent — it adds
the runtime validation that a dataclass deliberately omits — but reaching for
a dependency before you understand what `@dataclass` generates means you
cannot debug it when the generation is not what you assumed. Exercise 7 has
you rebuild the decorator yourself for exactly that reason.
