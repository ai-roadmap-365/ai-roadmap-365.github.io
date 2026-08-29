# Troubleshooting — Day 047 lab

## The two numbers concatenate instead of adding (I get `57`, not `12`)

`input()` and every item in `sys.argv` are **strings**, so `"5" + "7"` glues
them into `"57"`. Convert each to a number first with `float(...)` (or `int(...)`
for whole numbers) before doing arithmetic. This is the single most common
beginner bug in Python, and the whole reason `parse_pair` calls `float()`.

## The program hangs and prints nothing

You probably called `input()` in a context with no keyboard. When a program is
run inside an automated test or a pipeline with nothing piped in, `input()`
waits forever for a human who is not there. This lab avoids the trap by reading
`sys.argv` when an argument is present and `sys.stdin` otherwise — neither of
which blocks on a missing keyboard. If you press `Ctrl+D` (macOS/Linux) it sends
"end of input" and unblocks a waiting `sys.stdin.read()`.

## Testing an interactive program without typing

You do not need to type anything to test a program that reads standard input —
feed it with a pipe or a here-string:

```bash
echo "5 7" | python3 examples/io_demo.py        # pipe
python3 examples/io_demo.py <<< "5 7"            # bash here-string
printf '5 7\n' | python3 examples/io_demo.py     # printf for exact bytes
python3 examples/io_demo.py 5 7                   # or just pass arguments
```

This is exactly how the test script drives the program, which is why the tests
are fully non-interactive.

## My error message shows up mixed into the data / gets captured by a pipe

You printed the error to standard output. Diagnostics must go to standard error:
`print(f"error: {err}", file=sys.stderr)`. To watch the two channels separately:

```bash
python3 examples/io_demo.py 5 hello 1>/tmp/out.txt 2>/tmp/err.txt
cat /tmp/out.txt   # should be empty on bad input
cat /tmp/err.txt   # the error line
```

## `echo $?` shows `0` after bad input

You reported the error but did not signal failure. Return a non-zero code:
call `sys.exit(1)` (or, as in the reference, `return 1` from `main()` and
`sys.exit(main())`). Only a non-zero exit tells a shell or CI that the run
failed.

## The columns are ragged / decimals do not line up

A number without a format spec prints at its natural width, so columns wander.
Give every value in a column the same fixed-width, fixed-decimal spec, e.g.
`{value:>8.2f}` — `>` right-aligns, `8` sets the width, `.2f` fixes two
decimals. Mixing widths between rows is the usual cause.

## `command not found: python3`

Python 3 is not on your `PATH`. Install it (see `requirements/README.md`) or try
`python --version` — on some systems the command is `python`. Never assume;
check the version, because `python` sometimes still means Python 2.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and run the commands there), or run
the Python program directly in PowerShell (`python examples\io_demo.py 5 7`) and
skip the bash test script.
