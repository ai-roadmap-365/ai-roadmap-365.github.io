# Troubleshooting — Day 045 lab

## `python3: command not found`

Python 3 is not on your PATH. On macOS install it from python.org or with
Homebrew (`brew install python`); on Linux use your package manager
(`sudo apt install python3` on Debian/Ubuntu). On some systems the command is
just `python` — check with `python --version` and use whichever reports a 3.x
version.

## `UnicodeDecodeError` when reading the sample

You are reading the file with the wrong encoding, or the file was re-saved in
a non-UTF-8 encoding. The program passes `encoding="utf-8"` explicitly for
exactly this reason — always name the encoding when you read text, rather than
relying on the platform default (which differs between macOS, Linux, and
Windows). If you edited `sample.txt`, save it as UTF-8 or restore it with
`git checkout -- examples/sample.txt`.

## `SyntaxError` inside an f-string — usually about quotes

An f-string delimited with double quotes cannot contain an unescaped double
quote inside its `{...}` expression. Two easy fixes:

- Use single quotes inside a double-quoted f-string (or vice versa):
  `f"name is {d['key']}"`.
- Put the literal quote in the text part, not the expression:
  `f'Most common word:  "{word}"'` (single-quoted f-string, literal double
  quotes around the value).

Before Python 3.12 you also could not reuse the *same* quote character inside
the braces at all; if you are on an older Python, switch the inner quotes.

## `IndexError: list index out of range`

`lines[0]` or `words[1]` failed because the text was empty. Make sure
Exercise 1 actually read the file into `text` (the starter prints a reminder
and stops if `text` is still `None`).

## The table columns do not line up

The alignment comes from the format specs `:<{LABEL_WIDTH}` (left-align) and
`:>{VALUE_WIDTH}` (right-align). If a label is longer than `LABEL_WIDTH` it
pushes the number across; widen `LABEL_WIDTH` at the top of the file, or
shorten the label.

## Off-by-one in a slice

Remember `s[a:b]` includes index `a` but stops **before** `b`, so it has
`b - a` characters. `"River"[0:3]` is `"Riv"`, not `"Rive"`. Negative indices
count from the end: `s[-1]` is the last character.
