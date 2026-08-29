# Dependencies — Day 012 lab

**None beyond a POSIX shell.** This lab has no installable dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities: `basename`, `sort`, `uniq`, `printf`, `mktemp` — all
  part of the base system on macOS and Linux.

## Optional: ShellCheck

[ShellCheck](https://www.shellcheck.net/) is a free, open-source static
analyzer for shell scripts. It is **entirely optional** — the lab is fully
completable without it — but it is an excellent habit to adopt. If you want to
try it:

- macOS: `brew install shellcheck`
- Debian/Ubuntu: `sudo apt install shellcheck`
- Fedora: `sudo dnf install ShellCheck`

Then run `shellcheck examples/backup_notes.sh` to see it in action. There is no
paid version; ShellCheck is free.

The companion formatter **shfmt** (also free and open source) is likewise
optional — it rewrites a script into a consistent style — and is not needed to
finish the lab.

There is deliberately no `requirements.txt` or `package.json` here: this lab
runs on a factory-fresh macOS or Linux machine with nothing installed.
