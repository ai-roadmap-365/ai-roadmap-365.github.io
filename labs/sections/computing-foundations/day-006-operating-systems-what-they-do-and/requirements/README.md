# Dependencies — Day 006 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities only: `uname`, `date`, `uptime`, `whoami`, `df`,
  `ps`, `sort`, `head`, `awk`, `sed`, `ls`, `wc` — all part of the base
  system on macOS and Linux (and inside WSL).

Windows users need WSL (`wsl --install`) — a one-time setup that the rest
of this course relies on from Week 2 onward, so today is the right day to
do it.

There is deliberately no `requirements.txt`/`package.json` here; like Day 1,
this lab must run on a factory-fresh machine. Later labs declare their
Python or Node dependencies in this directory.
