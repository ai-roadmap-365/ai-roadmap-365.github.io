# Required behaviour (all platforms)

A correct run of `examples/venv_demo.sh` must, on any supported system:

1. Print the interpreter version (`Python 3.x.y`).
2. Create a `.venv` directory containing an `activate` script and its own
   `python` (in `.venv/bin/` on macOS and Linux, `.venv\Scripts\` on Windows).
3. Show `which python` pointing at the **global** interpreter before
   activation and at `.../.venv/bin/python` after activation.
4. Report `sys.prefix` as a path that ends in `.venv` — the proof of
   isolation — and print the `OK: ... the environment is isolated.` line.
5. Write a `requirements.txt` documenting the Python version and the
   standard-library-only note.
6. Deactivate and remove the temporary directory, leaving nothing behind.

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, Python 3.14.0, 2026-07-12).

## Platform differences (documented, not fabricated)

- **Temp path.** The working directory is created by `mktemp` and is random;
  every run prints a different path. macOS resolves `/var` to `/private/var`,
  so paths appear under `/private/var/folders/...`; Linux typically uses
  `/tmp/venv-demo.XXXXXX`.
- **Global interpreter path.** Before activation, `which python` reflects
  wherever your Python came from — e.g. `/opt/homebrew/...` (Homebrew on Apple
  Silicon), `/usr/bin/python3` (system), or a `pyenv` shim. Only the *change*
  on activation matters, not the exact path.
- **`.venv/bin` contents.** Newer Python versions add extra convenience
  symlinks (for example Python 3.14 adds a `𝜋thon` alias). The essential
  entries are `activate`, `python`, `pip`.
- **Windows.** Activation is `.venv\Scripts\activate` and the interpreter is
  `.venv\Scripts\python.exe`. Run the equivalent commands in PowerShell, or run
  the scripts unchanged inside WSL, where the Linux paths apply.
