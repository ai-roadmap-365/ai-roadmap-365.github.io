# Dependencies — Day 007 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities only: `ps`, `kill`, `sleep`, `wc`, `tail`, `tr`,
  `sed`, `date` — all part of the base system on macOS and Linux, and the
  shell built-ins `jobs`, `wait`, `trap`, and the `$!`/`$$` variables.

Windows users: run everything inside WSL (any distribution) — the scripts
use portable `ps -o` column syntax that works identically on macOS and
Linux. There is deliberately no `requirements.txt`/`package.json` here;
process control is an operating-system skill, not a library.
