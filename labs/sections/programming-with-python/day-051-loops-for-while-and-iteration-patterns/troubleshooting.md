# Troubleshooting — Day 051 lab

## The program seems to hang with no output

A data command (`total`, `filter`, `transform`, `search`, `histogram`) reads
its numbers from **standard input**. If you run it with nothing piped in, it
waits for you to type input. Either pipe data:

```bash
echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py total
```

or, if you started it bare, type numbers and press **Ctrl-D** to signal
end-of-input. The `demo` command needs no input — it uses a built-in sample.

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the five exercises. Each unfinished pattern
function raises `NotImplementedError` on purpose so you cannot mistake an
empty function for a working one. Replace each `raise NotImplementedError(...)`
line with the loop described in the comment above it. Once all five are done,
the file runs exactly like `examples/patterns.py`.

## `... is not a whole number`

The program validates input at the boundary: every token on standard input
must be an integer. A stray letter or punctuation mark (for example `1 x 3`)
is reported by name and the program exits non-zero, instead of crashing with
a raw traceback. Check your input for non-numeric tokens.

## `filter needs one threshold` / `search needs one target`

Those two commands take one number *after* the command name: `filter 4`,
`search 5`. Running them bare is rejected with a usage message. The number is
a command argument (read from `argv`), separate from the data on standard
input.

## My histogram bars look misaligned

Each value's label is right-aligned to the width of the widest value so the
`|` separators line up. Build each bar as `count` copies of `#`, and pad the
**label** (with `.rjust(width)`), not the bar. Verify on `1 2 2 3 3 3`, which
must give `1 | #`, `2 | ##`, `3 | ###`.

## `echo $?` shows `0` after a not-found search

The found and not-found search cases must end with **different** exit codes
(0 for found, non-zero for not found) so a caller can tell them apart. If both
return 0, re-check that the not-found path returns exit code 1.

## An infinite loop froze my terminal

If you experiment with a `while` loop and it never ends, press **Ctrl-C** to
interrupt it. The cause is almost always that nothing in the body makes the
condition move toward false — add the missing progress step (a counter
increment, or a reachable `break`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.
