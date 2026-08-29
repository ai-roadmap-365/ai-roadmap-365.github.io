# Dependencies — Day 043 lab

**Just Python 3 and a POSIX shell.** There are no PyPI packages to install and
no network access is required at any step — creating a virtual environment uses
only tools that ship with Python.

- `python3` **≥ 3.8** (any modern 3.x is fine; the `venv` module has shipped
  with Python since 3.3). Preinstalled on macOS and most Linux distributions.
- `bash` ≥ 3.2 (preinstalled on macOS and Linux).

## Checking what you have

```bash
python3 --version
```

If that prints `Python 3.x.y`, you are ready.

## If Python 3 is missing

Install it once, using the package-manager skills from Day 13:

- **macOS:** `brew install python` (Homebrew), or download the installer from
  the official python.org downloads page.
- **Debian/Ubuntu Linux:** `sudo apt update && sudo apt install python3 python3-venv`
- **Fedora Linux:** `sudo dnf install python3`
- **Windows:** install from the official python.org downloads page (tick "Add
  Python to PATH"), or use WSL and follow the Linux instructions.

On some minimal Debian/Ubuntu systems the `venv` module is packaged
separately — that is why `python3-venv` is listed above. If
`python3 -m venv .venv` complains that `venv` is unavailable, install that
package.

This lab installs nothing else. Later labs will declare their Python packages
in a `requirements.txt`, which is exactly the reproducibility habit this lesson
introduces.
