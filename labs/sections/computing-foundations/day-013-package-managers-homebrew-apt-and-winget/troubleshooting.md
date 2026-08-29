# Troubleshooting — Day 013 lab

## The script prints no `FOUND:` lines at all

None of the managers it looks for are on your `PATH`. This is a valid result,
and the script says so and still exits `0`. On macOS you may simply not have
Homebrew installed yet; on a minimal Linux system, try `command -v apt` on its
own to confirm apt is present.

## `brew: command not found`

Homebrew is not installed, or its directory is not on your `PATH`. This lab
**never installs anything**, so just record that brew is absent and inspect
whichever manager you do have. (If you later choose to install Homebrew, follow
the official instructions at the Homebrew documentation — outside this lab.)

## `pip` is missing but `pip3` is present (or vice versa)

On many systems the Python package manager is named `pip3`. The detector checks
both and reports whichever exists; treat a hit on either as "pip is available."

## `apt-cache policy` prints a lot of output

That command lists every configured repository and pinning rule. The script
indents it and shows only the first few lines with `head` — that is expected.
`apt-cache` is read-only and changes nothing.

## `Permission denied` when running the script

You do not need to make it executable — run it through bash explicitly:
`bash starter/detect_pkg_manager.sh`. If you prefer `./starter/...`, first run
`chmod +x starter/detect_pkg_manager.sh`.

## I am on Windows and `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path), or skip
the script and run the winget commands from the cheat sheet directly in
PowerShell (`winget --version`, `winget list`), filling the worksheet manually.

## The tests report a safety failure

The test suite statically scans both scripts for `sudo` and for
install/remove/upgrade commands and fails if it finds any. If you edited the
starter and added a changing command, remove it — every query in this lab must
be read-only.
