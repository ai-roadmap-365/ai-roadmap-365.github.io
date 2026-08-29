# Dependencies — Day 030 lab

**One tool: Git.** This lab needs nothing else beyond a POSIX shell.

- `git` (any 2.x version; the reference run used 2.50.1). Check with
  `git --version`.
- `bash` ≥ 3.2 and the standard utilities `mktemp`, `printf`, `sed`, `grep`,
  `ls`, `rm` — all preinstalled on macOS and every mainstream Linux
  distribution.

## Installing Git

- **macOS:** `git` ships with the Xcode Command Line Tools. If `git --version`
  prompts to install them, accept — or install Git via Homebrew
  (`brew install git`).
- **Debian/Ubuntu:** `sudo apt install git`
- **Fedora/RHEL:** `sudo dnf install git`
- **Windows:** install Git for Windows, or run this lab inside WSL and follow
  the Linux path.

There is deliberately no `requirements.txt`/`package.json` here: the lab is
pure Git and shell. It makes **no network connections** and needs **no API
key**. It never writes to your global Git configuration — every command runs
with a local identity scoped to a throwaway repository the script deletes on
exit.
