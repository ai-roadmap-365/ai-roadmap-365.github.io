# Dependencies — Day 039 lab

This lab needs only a POSIX shell and the `sqlite3` command-line tool.

- **`bash`** ≥ 3.2 — preinstalled on macOS and every mainstream Linux
  distribution.
- **`sqlite3`** — the embedded relational database used in step 2.
  - **macOS:** preinstalled. Confirm with `sqlite3 --version`.
  - **Debian/Ubuntu:** `sudo apt install sqlite3` if it is missing.
  - **Fedora/RHEL:** `sudo dnf install sqlite`.
  - **Windows:** use WSL and install `sqlite3` inside it as on Linux.
- **`shasum` or `sha256sum`** — for the object-storage content key. One of
  these is always present on macOS and Linux; the scripts pick whichever
  exists, and both produce the same SHA-256 value.

There is deliberately no `requirements.txt`/`package.json`: the lab installs
nothing beyond the `sqlite3` package above and runs fully offline. No network
access and no API keys are required.
