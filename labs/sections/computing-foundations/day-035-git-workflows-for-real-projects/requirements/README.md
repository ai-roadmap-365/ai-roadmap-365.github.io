# Dependencies — Day 035 lab

**Just git and a POSIX shell.** This lab has no installable dependencies:

- `git` (2.23 or newer — for the `git switch` command; any git from the last
  few years works). Check with `git --version`.
- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution).
- Standard OS utilities used by the scripts: `mktemp`, `printf`, `grep`, `awk`,
  `sed` — all part of the base system.

There is no `requirements.txt` or `package.json`, no account, and no API key.
Every git operation runs against a **local bare repository** created in a
temporary directory, so the lab needs **no network connection** at all.

If `git` is missing:

- **macOS:** `xcode-select --install` (installs the command-line tools), or
  install git from your package manager of choice.
- **Debian/Ubuntu:** `sudo apt install git`.
- **Fedora:** `sudo dnf install git`.
