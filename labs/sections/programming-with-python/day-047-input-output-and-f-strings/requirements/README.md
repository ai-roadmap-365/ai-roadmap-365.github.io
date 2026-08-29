# Dependencies — Day 047 lab

**Only Python 3 and a POSIX shell.** This lab has no installable dependencies:

- `python3` (version 3.6 or newer — f-strings and their format specs work on
  every supported Python; the authoring machine used Python 3.14). Check with
  `python3 --version`.
- `bash` (preinstalled on macOS and every mainstream Linux distribution) to run
  the test script.
- Standard shell utilities used by the tests only: `echo`, `printf`, `grep`,
  `mktemp` — all part of the base system.

The program itself imports only `sys` from the Python standard library, so there
is deliberately no `requirements.txt` here. Everything runs offline, needs no
account or API key, and needs no elevated privileges.

## Installing Python (if needed)

- **macOS:** `brew install python` (Homebrew) or download from the official
  python.org installer. macOS may already ship a `python3`.
- **Linux:** `sudo apt install python3` (Debian/Ubuntu) or the equivalent for
  your distribution; most ship Python 3 already.
- **Windows:** install Python from the Microsoft Store or python.org, or use WSL
  and follow the Linux path.
