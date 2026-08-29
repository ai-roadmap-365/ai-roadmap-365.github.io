# Dependencies — Day 031 lab

**One tool: `git`.** Nothing else is installed, downloaded, or configured.

- `git` ≥ 2.23 (for `git switch`; released August 2019). Check with
  `git --version`. On older git, the lab still works with `git checkout`
  substitutions documented in `troubleshooting.md`.
- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
  and the standard utilities `mktemp`, `printf`, `sed`, `grep` — all part of
  the base system.

There is deliberately no `requirements.txt` or `package.json`: the lab creates
a throwaway repository in a temporary directory and needs no project of its
own.

## Installing git (if `git --version` fails)

- **macOS:** `xcode-select --install` (installs the Command Line Tools, which
  include git), or install from the official git website.
- **Debian/Ubuntu:** `sudo apt update && sudo apt install git`
- **Fedora:** `sudo dnf install git`
- **Windows:** install Git for Windows, or run this lab inside WSL and use the
  Linux path.

No network access is required to run the lab itself — only, possibly, to
install git the first time.
