# Troubleshooting — Day 038 lab

## `grep: invalid option` or my metacharacters are treated literally

You almost certainly omitted `-E`. Basic `grep` (BRE) requires a backslash
before `+`, `?`, `{`, `(`, and `|` to make them special; `grep -E` (extended,
ERE) treats them as special directly. Every pattern in this lab assumes `-E`.

## `sed` errors on macOS but the same command works on Linux (BSD vs GNU)

macOS ships **BSD sed**; most Linux distributions ship **GNU sed**. They differ:

- **`-E` for extended regex:** both accept `-E`. (GNU also accepts `-r`; BSD
  does not. Use `-E` for portability — this lab does.)
- **In-place editing:** GNU is `sed -i 's/…/…/' file`; BSD requires an argument,
  `sed -i '' 's/…/…/' file`. This lab never edits files in place, so you will
  not hit this, but it is the most common cross-platform `sed` surprise.
- **Shorthands:** GNU sed understands `\+`, `\?`, and (in some builds) `\d`;
  BSD sed does not. This lab uses only `[0-9]`, `[[:alpha:]]`, and explicit
  `{n}` counts, which behave the same on both.

If a `sed` command from elsewhere fails on macOS, first rewrite any `\d` as
`[0-9]` and any `\+` as `+` under `-E`.

## `\d` matches nothing

Many command-line tools do not support the PCRE shorthand `\d`. Use `[0-9]` or
the POSIX class `[[:digit:]]`. The `\d`, `\w`, `\s` shorthands live in Python
and JavaScript, not in every `grep`/`sed`.

## The IP or status-code pattern matches something unexpected

This is the "too loose" failure mode and it is the whole point of the lab. For
example, `[0-9]{3}$` matches the last three digits of a phone number as well as
a status code — that is why Exercise 2 first *selects* log lines with
`" [0-9]{3}$` before extracting. Tighten the pattern or add context (a
neighbouring literal, an anchor) until it matches only what you mean.

## `Permission denied` when running a script

Run it through bash explicitly: `bash starter/regex_drills.sh`. You do not need
to `chmod +x` anything. If you prefer `./starter/regex_drills.sh`, first run
`chmod +x starter/regex_drills.sh`.

## The sed date reformat prints the input unchanged

Your pattern did not match, so `sed` left the line alone. Check that the field
counts match the input exactly (`{4}` vs `{2}`) and that you used `#` as the
delimiter so the slashes in the date do not clash with `sed`'s syntax:
`sed -E 's#([0-9]{4})/([0-9]{2})/([0-9]{2})#\1-\2-\3#'`.

## Windows

Use WSL (`wsl --install`, then open Ubuntu) and follow the Linux path, or use
Git Bash. The GNU tools inside WSL behave exactly as described for Linux.
