# Dependencies — Day 038 lab

**None beyond a POSIX shell with `grep` and `sed`.** This lab has zero
installable dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- `grep` with the `-E` (extended regex) option — preinstalled everywhere
- `sed` with the `-E` (extended regex) option — preinstalled on macOS (BSD sed)
  and Linux (GNU sed)

There is deliberately no `requirements.txt`/`package.json`: every tool used
ships with the operating system, nothing reaches the network, and no account or
API key is required. The lab only *reads* the committed sample file and prints
to your terminal.

If `grep -E` or `sed -E` is somehow missing (extremely minimal containers),
install `grep` and `sed` from your package manager (`apt install grep sed` on
Debian/Ubuntu). See `../troubleshooting.md` for BSD-vs-GNU differences.
