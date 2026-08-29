# Dependencies — Day 029 lab

**Just `git` and a POSIX shell.** This lab has no installable project
dependencies and needs no network, account, or API key.

- `bash` (3.2 or newer — preinstalled on macOS and every mainstream Linux
  distribution).
- `git` (2.x). Checking whether you already have it:

  ```bash
  git --version
  ```

If that prints a version, you are ready. If it says `command not found`,
install git — it is free and open source on every platform:

- **macOS:** ships with the Command Line Tools. Install them with
  `xcode-select --install`, or install git via Homebrew: `brew install git`.
- **Debian/Ubuntu Linux:** `sudo apt update && sudo apt install git`
- **Fedora/RHEL Linux:** `sudo dnf install git`
- **Windows:** install Git for Windows (which includes Git Bash), or run the
  lab inside WSL and use the Linux instructions.

Standard utilities the scripts use — `mktemp`, `printf`, `cat`, `grep`,
`sed`, `awk` — are part of the base system on macOS and Linux. `git restore`
needs git 2.23 or newer; on older git the scripts fall back to `git checkout`
automatically, so any 2.x release works.
