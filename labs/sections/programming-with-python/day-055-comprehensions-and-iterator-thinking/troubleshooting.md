# Troubleshooting — Day 055 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot accidentally think an
empty function "works." Replace each `raise NotImplementedError(...)` line
with the real body described in the comment above it. Once all five
exercises are done, the file prints exactly what the reference does.

## `TypeError: 'generator' object is not subscriptable`

You tried to index a generator, like `gen[0]`. Generators have no indexing
and no length — they only produce items on demand. Use `next(gen)` to pull a
single item, or `list(gen)` to materialize them all into a list (only safe
when the stream is small enough to fit in memory).

## My set line prints in a different order each run

Sets are unordered, so their `repr` is not stable to compare. The reference
prints the set through `sorted(...)` for exactly this reason. If you compare
distinct-teams output, sort it first.

## My pipeline prints nothing, or a wrong average

A generator is **single-use**: after one full pass it is exhausted and yields
nothing more. If you consumed the pipeline once already — for example in a
debug `print(list(pipeline))` — rebuild it before the real computation.
Assemble the pipeline fresh (`scores(only_team(read_records(rows), team))`)
immediately before you loop over it.

## `only_team` returns a list instead of streaming

If you wrote `return [...]` or built a list with `append`, the function is no
longer lazy — it materializes everything. Use `yield r` inside the loop so
the function becomes a generator that hands out one record at a time. The
test checks that `only_team(...)` is a real generator object.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.

## The two averages do not match, and the program crashes on the `assert`

That is the program catching a real bug for you. The lazy pipeline and the
loop baseline must compute the same number; if the `assert` fails, one of
them filters or sums differently. Re-check that `only_team` keeps exactly the
records whose `team` matches, and that `average_score_lazy` divides the total
by the count of records it actually saw.
