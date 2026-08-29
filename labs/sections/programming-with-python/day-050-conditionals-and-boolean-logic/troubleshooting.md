# Troubleshooting — Day 050 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and most
Linux systems, bare `python` may be missing or point to an old version. Check
with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function raises
`NotImplementedError` on purpose so you cannot accidentally think an empty
function "works." Replace each `raise NotImplementedError(...)` line with the
real body described in the comment above it. Once all five exercises are done,
the file runs like the reference.

## `SyntaxError` pointing at an `if` line — `=` versus `==`

If you wrote `if status = "verified":` Python raises a `SyntaxError`, because
`=` **assigns** and cannot appear in a condition. Use `==` to **compare**:
`if status == "verified":`. This is one of the few beginner bugs Python turns
into a hard error rather than a silent one — be grateful, and fix the operator.

## A boundary case gives the wrong category

Check whether you meant `<` or `<=`. In this engine `score >= 0.9` accepts
exactly 0.9, and `score < 0.5` rejects everything below 0.5 but keeps 0.5
itself. Trace the boundary values `0.0`, `0.5`, `0.9`, and `1.0` by hand and
compare with the table in `expected-output/FIELDS.md`.

## The high-confidence branch never runs

You probably tested the broader condition first. In an `if`/`elif` ladder the
first true branch wins, so if `score >= 0.5` comes before `score >= 0.9`, the
`>= 0.9` branch is unreachable. Put the most specific (or most exceptional) test
first. In `classify`, the guard `score < 0.5` is checked first on purpose.

## `ModuleNotFoundError: No module named 'triage'`

Python imports a module by searching `sys.path`, which does not include the
`examples/` subfolder by default. The import one-liners in this lab add it
first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from triage import classify; print(classify(0.95, True))"
```

Run this from the lab directory (the folder that contains `examples/`), not from
inside `examples/` itself.

## Importing the file runs the whole program

This is exactly the problem the main guard prevents. If importing your module
prints output or exits, you either forgot `if __name__ == "__main__":`
(Exercise 5) or wrote program-running code at the top level instead of inside
`main`. Only the guarded `sys.exit(main(sys.argv))` should trigger execution.

## `echo $?` shows `0` after a bad input

Your `main` is not returning `2` on the error path, or you are not passing its
return value to `sys.exit()`. The guard must read `sys.exit(main(sys.argv))`,
and `main` must `return 2` after printing an error. The exit code is how other
programs detect that yours refused the input.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.
