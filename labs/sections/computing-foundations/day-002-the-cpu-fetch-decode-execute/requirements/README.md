# Dependencies — Day 002 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux
  distribution; on Windows, use WSL).
- Standard utilities the scripts call: `tr`, `grep`, `sed`, `mktemp`,
  `dirname` — all part of the base system on macOS and Linux.

There is deliberately no `requirements.txt`/`package.json` here: the toy
CPU is a single readable shell script, because the point of the lab is
that you can see every moving part. Later labs declare their Python or
Node dependencies in this directory.
