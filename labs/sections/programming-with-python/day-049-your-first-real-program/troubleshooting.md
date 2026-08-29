# Troubleshooting — Day 049 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot accidentally think an
empty function "works." Replace each `raise NotImplementedError(...)` line
with the real body described in the comment above it. Once all five
exercises are done, the file runs like the reference.

## `ModuleNotFoundError: No module named 'converter'`

Python imports a module by looking on its search path (`sys.path`), which
does not include the `examples/` subfolder by default. The import one-liners
in this lab add it first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from converter import celsius_to_fahrenheit; print(celsius_to_fahrenheit(100))"
```

Run this from the lab directory (the folder that contains `examples/`), not
from inside `examples/` itself. If you `cd examples` first, use
`sys.path.insert(0, '.')` instead.

## Importing the file runs the whole program

This is exactly the problem the main guard prevents. If importing your
module prints output or exits, you either forgot
`if __name__ == "__main__":` or wrote program-running code at the top level
(outside any function) instead of inside `main`. Only the guarded
`sys.exit(main(sys.argv))` should trigger execution. This is why "importing
vs running" matters: a well-guarded file can be *imported* to test its
functions and *run* to do its job, and the two never interfere.

## Testing without a human: how the tests stay non-interactive

This program takes its input from command-line arguments, never by
prompting. That is deliberate: a program that reads `input()` from a human
cannot be tested automatically, because a test has no one to type. Because
the converter reads `sys.argv`, a test can simply run
`python3 examples/converter.py 100 C` and check the output and exit code —
no interaction required. If you extend the program, keep input on the
command line (or read from a file) so it stays testable.

## `echo $?` shows `0` after a bad input

Your `main` is not returning `1` on the error path, or you are not passing
its return value to `sys.exit()`. The guard must read
`sys.exit(main(sys.argv))`, and `main` must `return 1` after printing an
error. The exit code is how other programs detect that yours failed.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing
it directly: `bash tests/run_tests.sh`. You do not need to `chmod +x`
anything.

## A conversion looks wrong

Check operator precedence: the Celsius-to-Fahrenheit formula is
`celsius * 9 / 5 + 32`, and Python evaluates `*` and `/` before `+`. Verify
by hand with a known value — 100 °C is 212 °F, 0 °C is 32 °F.
