# Dependencies — Day 041 lab

**Only a POSIX shell and git.** This lab deliberately has zero installable
dependencies beyond what a developer machine already has:

- `bash` ≥ 3.2 — preinstalled on macOS and every mainstream Linux distribution.
- `git` — the version-control tool from Week 5. Check with `git --version`.
- Standard utilities used by the scripts: `mktemp`, `grep`, `printf`, `chmod`,
  and `bash -n` — all part of the base system.

No Python, Node, package installs, network access, API keys, or `sudo` are
required. Every script runs entirely inside a temporary directory it creates and
deletes, so it changes nothing on your machine.

If `git` is missing:

- **macOS:** `xcode-select --install` (installs the command-line developer tools, including git).
- **Debian/Ubuntu:** `sudo apt install git`.
- **Fedora:** `sudo dnf install git`.
