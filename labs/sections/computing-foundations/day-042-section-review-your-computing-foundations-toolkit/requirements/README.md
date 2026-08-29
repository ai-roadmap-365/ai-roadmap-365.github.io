# Dependencies — Day 042 lab

This lab checks for the core Course 1 toolkit on your machine; it does not
install anything. The check itself needs only a POSIX shell:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard utilities the check calls: `uname`, `date`, `command`, `mktemp`,
  `printf`, `grep`, `wc`, `tr` — all part of the base system.

The tools the check *looks for* are the section's toolkit. They are not
required for the script to run (it degrades gracefully when one is missing),
but you will want them for the rest of the course:

| Tool | Course 1 day | Install if missing |
| ---- | ------------- | ------------------ |
| a shell | Day 8 | Already present — it is running the script |
| `git` | Days 29-35 | `brew install git` / `apt install git` (Day 13 covered package managers) |
| `curl` | Day 21 | `brew install curl` / `apt install curl` |
| `python3` | Day 15+ | `brew install python` / `apt install python3` |
| `sqlite3` | Day 39 | `brew install sqlite` / `apt install sqlite3` |
| an editor | Day 36 | `brew install vim`/`nano`, or set `$EDITOR` |

There is deliberately no `requirements.txt`/`package.json`: this capstone
must run on any machine that finished Course 1, including one with gaps.
