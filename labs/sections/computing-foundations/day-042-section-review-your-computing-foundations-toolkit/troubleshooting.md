# Troubleshooting — Day 042 lab

This lab is a readiness report, so most "problems" are really the report doing
its job: surfacing a gap and pointing you to the day that fixes it. Use this
table to turn each `[--]` line into a plan.

## A tool shows `[--]` (not found) — which day fixes it?

| Missing tool | Revisit | What to do |
| ------------ | ------- | ---------- |
| `git` | Days 29-35 | Install git (Day 13 covered package managers), then redo Day 30's commit flow |
| `curl` | Day 21 | Install curl; Day 21 shows how to inspect traffic with it |
| `python3` | Day 15+ | Install python3 — Course 2 needs it; the machine/OS week (1-7) covers what an install is |
| `sqlite3` | Day 39 | `brew install sqlite` / `apt install sqlite3`; Day 39 explains when a database beats a file |
| `editor` (unset `$EDITOR`, none on PATH) | Day 36 | Choose and configure an editor, then `export EDITOR=<your-editor>` |

## A skill check shows `[--]`

- **`git init + commit works` failed.** git is likely missing or unusually
  configured. The check supplies its own identity with `-c user.name`/`-c
  user.email`, so a missing global config is not the cause — revisit Days
  29-30. Run `git --version` to confirm git is installed.
- **`shell pipeline works` failed.** One of `grep`, `wc`, or `tr` is missing
  or your shell is very non-standard. Revisit Days 10-12 on text tools and
  pipes; on minimal containers install `coreutils`.
- **`sqlite query works` failed.** `sqlite3` is missing (see the table above)
  or an old build. Revisit Day 39.

## `sqlite3: command not found`

SQLite ships with macOS and most Linux installs; if it is absent the check
reports it as a gap rather than crashing. Install it with your package
manager (Day 13) — `brew install sqlite` or `apt install sqlite3`.

## `editor` shows as unset

You have no `$EDITOR` environment variable and no common editor was found on
your `PATH`. That is exactly the situation Day 36 addresses: install and
configure an editor, then set `export EDITOR=<name>` in your shell profile
(Day 11 covered shell configuration).

## The git skill check left a folder behind

It should not — it builds the throwaway repo under a temporary directory
(`mktemp -d`) and removes it. If you interrupted the script mid-run, delete
any leftover `toolkit-check-tmp.*` directory in your system temp folder
(`$TMPDIR` on macOS, `/tmp` on Linux).

## `Permission denied` when running the script

Run it through bash explicitly (`bash starter/toolkit_check.sh`) rather than
`./starter/toolkit_check.sh`. If you prefer the latter, make it executable
first with `chmod +x starter/toolkit_check.sh`.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path), or run
the individual tool-version commands manually in PowerShell (`git --version`,
`curl --version`, `python --version`) and fill the worksheet by hand.
