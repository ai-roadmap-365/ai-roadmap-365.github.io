# Dependencies — Day 010 lab

**None beyond a POSIX shell and the standard text tools.** Everything this lab
uses is preinstalled on macOS and every mainstream Linux distribution:

- `bash` ≥ 3.2 — to run the scripts.
- `cat`, `head`, `tail`, `wc` — viewing and counting text.
- `grep` — searching lines by pattern.
- `sed` — stream editing and substitution.
- `awk` — field extraction (pulling out the IP, path, and status columns).
- `sort`, `uniq`, `cut`, `tr` — ordering, de-duplicating, and trimming.

All of these are part of the base system (GNU coreutils / util-linux on
Linux, the BSD equivalents on macOS). There is deliberately no
`requirements.txt` or `package.json`: this lab must run on a factory-fresh
machine with nothing installed.

## Optional (not required)

- `ripgrep` (`rg`) is a fast, free, open-source alternative to `grep`. The
  lesson mentions it, but this lab never depends on it — every exercise uses
  the always-present `grep`.

## Windows

Use **WSL** (Windows Subsystem for Linux): `wsl --install`, open Ubuntu, and
run the lab exactly as written. The native PowerShell shell has different text
tools and is not covered here.
