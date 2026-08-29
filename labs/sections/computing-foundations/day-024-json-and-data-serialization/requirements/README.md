# Dependencies — Day 024 lab

**Only `python3`, which is preinstalled on macOS and every mainstream Linux
distribution.** This lab is deliberately offline and dependency-light:

- `python3` (3.x) — provides `python3 -m json.tool` (validate and
  pretty-print) and the `json` module used by the one-line extractors. No
  third-party packages are installed.
- `bash` (3.2 or newer) — runs the lab scripts. Preinstalled on macOS and
  Linux.

## Optional

- `jq` — a dedicated command-line JSON processor. The lab's scripts show the
  `jq` equivalent of each `python3` step as a comment, so you can compare the
  two styles, but **every required step uses `python3` only**. Install `jq`
  from your package manager if you want to try the commented commands
  (`brew install jq` on macOS, `apt install jq` on Debian/Ubuntu).

## Platform notes

- **macOS / Linux:** nothing to install.
- **Windows:** run the scripts inside WSL (Windows Subsystem for Linux) so
  `bash` and `python3` behave as documented, or install Python 3 for Windows
  and run the individual `python3` commands from the lesson by hand.
- If `python3` is not found but `python` is, and `python --version` reports
  3.x, substitute `python` for `python3` throughout.
