# Dependencies — Day 011 lab

**None beyond a POSIX shell.** This lab has zero installable dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities: `tr`, `sed`, `grep`, `id`, and the shell builtins
  `echo`, `export`, `alias`, `type`, and `command` — all part of the base
  system.

The scripts only **read** environment information and print it. They make no
network connections, need no elevated privileges, and write nothing outside
their own console output.

There is deliberately no `requirements.txt`/`package.json` here. Later labs
that use Python or Node declare their dependencies in this directory.
