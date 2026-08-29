# Dependencies — Day 009 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities: `mktemp`, `mkdir`, `touch`, `cp`, `mv`, `rm`, `ls`,
  `chmod`, `pwd`, and `find` — all part of the base system.

There is deliberately no `requirements.txt`/`package.json` here; the lab must
run on a factory-fresh machine. Windows users run the scripts inside WSL
(Windows Subsystem for Linux), which provides the same utilities.
