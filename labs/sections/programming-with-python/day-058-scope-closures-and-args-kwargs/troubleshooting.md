# Troubleshooting — Day 058 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot mistake an empty
function for a working one. Replace each `raise NotImplementedError(...)`
line with the real body described in the comment above it. Once all five
exercises are done, the file behaves like the reference.

## `UnboundLocalError: local variable 'count' referenced before assignment`

Your inner `counter` function assigns to `count` (with `count += step`), but
you did not declare `nonlocal count`. Without it, Python treats `count` as a
brand-new local for the whole inner function, so reading it before the local
is assigned fails. Add `nonlocal count` as the first line inside `counter`.

## Both of my counters advance together

Each `make_counter` call must create its own `count` inside the function body
(`count = start`). If you captured a module-level variable or otherwise shared
one variable across calls, every returned closure updates the same state. The
fix is to keep `count` a local of `make_counter`, so each call gets a fresh,
independent one.

## `average(1, 2, 3, 4)` gave `2.5`, not a rounding change

That is correct. `ndigits` is **keyword-only** because it sits after
`*numbers`, so the `4` is treated as another number to average
((1+2+3+4)/4 = 2.5), not as the number of digits. To set the rounding you
must pass it by name: `average(1, 2, 3, 4, ndigits=1)`.

## `build_request` ignores my overrides

You merged the dictionaries in the wrong order. Write
`{**DEFAULTS, **kwargs}` so the caller's `kwargs` are spread **last** and
therefore win. `{**kwargs, **DEFAULTS}` would let the defaults overwrite the
caller's values, which is the opposite of what you want.

## `TypeError: build_request() got an unexpected keyword argument 'temperature'`

Your signature is missing the `**kwargs` parameter, so extra keyword
arguments have nowhere to be gathered. Make the signature
`def build_request(prompt, **kwargs):` — the `**kwargs` must be there to
accept arbitrary named options.

## `ModuleNotFoundError: No module named 'flexible'` in an import one-liner

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` subfolder by default. The import one-liners add it
first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from flexible import make_counter; print(make_counter()())"
```

Run it from the lab directory (the folder that contains `examples/`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
