# Troubleshooting — Day 043 lab

## `python3: command not found`

Python 3 is not installed or not on your `PATH`. See `requirements/README.md`
for the one-line install for your system. On Windows, `python` (not `python3`)
is often the command; if `python --version` shows a 3.x version, use `python`
in place of `python3` for the venv-creation step.

## `python` vs `python3` confusion

Outside a virtual environment, prefer `python3` — on some systems `python`
still means the old Python 2, or does not exist at all. **Inside** an active
venv, `python` is correct and points at the venv's interpreter. When in doubt,
run `which python` (macOS/Linux) or `where python` (Windows) to see exactly
which interpreter you are calling.

## `python3 -m venv` fails with "ensurepip is not available"

On some minimal Debian/Ubuntu installs the `venv` support is a separate
package. Install it: `sudo apt install python3-venv`. No other lab step needs
elevated privileges.

## `source .venv/bin/activate` — "no such file or directory"

Either you are not in the folder that contains `.venv`, or the environment did
not build. List it: `ls .venv/bin/` should show an `activate` file. On
**Windows** the activation path is different:

- PowerShell: `.venv\Scripts\Activate.ps1`
- Command Prompt: `.venv\Scripts\activate.bat`

If PowerShell blocks the script with an execution-policy error, run it inside
WSL instead, where the Linux commands apply unchanged.

## Activation "doesn't work" — `which python` looks the same

Activation only affects the shell you run it in. If you opened a new terminal
tab or ran the script in a subshell, activate again in the shell you are
actually using. Also note: some shells do not show the `(.venv)` prompt marker
even when the venv is active — trust `which python` and `sys.prefix`, not the
prompt text.

## Should I commit `.venv` to git?

No. A virtual environment is large, machine-specific, and fully rebuildable.
Add it to your `.gitignore`:

```text
.venv/
```

Commit your `requirements.txt` instead — that is the portable recipe that lets
anyone rebuild an identical environment.

## The tests report a failure

Run `bash tests/run_tests.sh` and read which line says `FAIL`. Each check names
exactly what it verified (venv created, `sys.prefix` inside the venv, cleanup,
the example script). The most common cause is a Python that is too old or a
missing `python3-venv` package — fix that first, then re-run.
