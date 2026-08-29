# Week 02 project — Personal Automation Script

Week 2 turned the terminal into your workshop: navigating, processing text,
configuring your environment, writing scripts, and scheduling them. This
project combines all of it into one small tool you will actually use.

## What you are building

A shell script that automates a real, repetitive task on your own machine —
and (optionally) a schedule to run it unattended. The canonical choice: a
**downloads/desktop organizer** that sorts a messy folder into subfolders by
file type and date, with a dry-run mode and a log. You may pick a different
task (a backup, a report generator, a batch renamer) as long as it meets the
requirements below.

## Requirements

Your script must use, and demonstrate, the Week 2 skills:

- A `#!/usr/bin/env bash` shebang and `set -euo pipefail` (Day 12).
- At least one **argument** with a sensible default, quoted correctly (Day 12).
- A **conditional** and a **loop** (Day 12).
- **Text processing** — group/count/sort with the tools from Day 10.
- A **`--dry-run`** flag that changes nothing (Day 14).
- **Logging** of what it did, with timestamps (Day 14).
- **Idempotency** — running it twice does no harm (Day 14).
- A short **README** explaining how to run it and one **cron line** (from
  Day 14) that would schedule it, written but not necessarily installed.

Start from the Day 14 lab's `organize_files.sh` and extend it, or write your
own from the Day 12 scripting patterns.

## Steps

1. Choose your task and copy the Day 14 organizer as a starting point (or
   start fresh).
2. Add or confirm: argument + default, dry-run, logging, idempotency.
3. Test it on a **copy** of real data (never your only copy) — dry-run first.
4. Write the README and the cron schedule line.
5. Validate against the checklist below.

## Expected output

- Running with `--dry-run` prints the planned actions and moves/changes
  nothing.
- Running for real performs the task and appends timestamped lines to a log
  file.
- Running it a second time reports "nothing to do" (or equivalent) and makes
  no further changes.
- A README with the exact run command and one valid cron expression.

## Validation

- [ ] Script has the shebang and `set -euo pipefail`.
- [ ] `--dry-run` provably changes nothing (check with `ls`/a diff before and
      after).
- [ ] A second real run is a no-op (idempotent).
- [ ] The log file records each action with a timestamp.
- [ ] The README's cron expression is valid (decode its five fields) and
      matches the stated schedule.
- [ ] You ran it on real data without losing anything (you worked on a copy).

## Troubleshooting

- Test on a throwaway directory first; never point a first draft at your only
  copy of anything.
- If the second run duplicates work, your move/skip logic is not idempotent —
  guard each action with a "does the target already exist?" check.
- Decode your cron line field by field (minute hour day month weekday) against
  the Day 14 table before trusting it.
