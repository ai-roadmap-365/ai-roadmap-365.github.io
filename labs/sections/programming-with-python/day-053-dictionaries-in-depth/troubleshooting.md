# Troubleshooting — Day 053 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version` — you need 3.7 or newer for the insertion-order
behaviour this lab relies on.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot accidentally think an
empty function "works." Replace each `raise NotImplementedError(...)` line with
the real body described in the comment above it. Once all four exercises are
done, the file runs like the reference.

## `KeyError` while counting

You read `counts[word]` before the key exists. The very first time a word is
seen, its key is not in the dictionary yet, so the square-bracket read raises
`KeyError`. Use the idiom instead:

```python
counts[word] = counts.get(word, 0) + 1
```

`counts.get(word, 0)` returns the running count, or `0` for a first-seen word,
so no key ever has to be created by hand and no `KeyError` is raised.

## `TypeError: unhashable type: 'list'`

You tried to use a list (or a set, or another dict) as a dictionary key. Keys
must be **hashable**, meaning immutable — a string, a number, or a tuple of
those. Use one of those as the key. In this lab the keys are words and roles
(strings), so this error usually means a variable holds the wrong thing.

## Counts come out in the wrong order

A plain dictionary preserves **insertion** order (the order words first
appeared), not alphabetical order. In this lab that is exactly what you want:
`the` prints before `cat` because it was seen first. If you sorted the output,
remove the sort; if you want alphabetical order for some other purpose, add
`sorted(...)` explicitly — the two are different on purpose.

## `most common` is wrong when two words tie

The rule is that the word seen **first** wins a tie. That falls out of using a
**strictly**-greater test (`n > best_count`) as you scan: an equal count never
displaces the earlier word. If you used `>=`, a later word would wrongly win.

## `ModuleNotFoundError: No module named 'wordstats'`

Python imports a module by looking on its search path (`sys.path`), which does
not include the `examples/` subfolder by default. The import one-liner in this
lab adds it first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from wordstats import count_words; print(count_words('a b a'))"
```

Run this from the lab directory (the folder that contains `examples/`), not
from inside `examples/` itself.

## Importing the file runs the whole program

This is what the main guard prevents. If importing your module prints output or
exits, you either removed `if __name__ == "__main__":` or wrote
program-running code at the top level instead of inside `main`. Only the
guarded `sys.exit(main(sys.argv))` should trigger execution — that is what lets
a test import `count_words` without launching the program.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.
