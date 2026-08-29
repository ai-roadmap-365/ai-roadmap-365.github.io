# Expected report fields (all platforms)

A correct run of `detect_pkg_manager.sh` prints, in order:

1. `=== Package Manager Report ===`
2. `Generated on: YYYY-MM-DD`
3. `Operating system kernel: <Darwin | Linux | ...>`
4. Zero or more `FOUND: <manager> -> <path>` blocks, each followed by one or
   more indented `read-only query:` lines and their output.
5. A summary line: either `Detected <n> package manager(s) above ...` or
   `No package managers detected on this machine.`
6. `=== End of report ===`

The script always exits `0`.

## What differs by platform

- **macOS:** typically finds `brew` (if installed) and, when Python/Node are
  present, `pip`/`pip3` and `npm`. Never finds `apt`, `apt-get`, or `winget`.
  `sample-macos.txt` in this directory is a real captured run (macOS, Apple
  Silicon, 2026-07-12): it found `brew`, `pip`, and `npm`.
- **Debian/Ubuntu Linux:** finds `apt` and `apt-get`; the read-only query is
  `apt-cache policy`, which lists the configured repositories without changing
  anything. May also find `pip3`/`npm`. Never finds `brew` (unless separately
  installed) or `winget`.
- **Windows (PowerShell/WSL):** in native PowerShell you would check
  `winget --version` and `winget list`. Under WSL the script runs as on Linux.

No matter the platform, the script installs, removes, and upgrades **nothing**.
A run that finds no managers at all is a valid outcome and still exits `0`.
