# Dependencies — Day 001 lab

**None beyond a POSIX shell.** This lab intentionally has zero installable
dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities: `uname`, `date`, `df`, plus `sysctl`/`sw_vers` on
  macOS or `lscpu`/`nproc` and the `/proc/meminfo`, `/etc/os-release` files
  on Linux — all part of the base system.

There is deliberately no `requirements.txt`/`package.json` here; the first
lab must run on a factory-fresh machine. Later labs declare their Python or
Node dependencies in this directory.
