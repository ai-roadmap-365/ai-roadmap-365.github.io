# Security notes — Day 014 lab

- **The script only touches the directory you give it.** `organize_files.sh`
  operates strictly inside its target folder: it creates extension subfolders
  there and moves that folder's files into them. It makes **no network
  connections**, needs **no elevated privileges**, and changes **no system
  setting**.
- **This lab never edits your crontab.** You read about cron, launchd, systemd
  timers, and Task Scheduler, and you write schedules on paper in the
  worksheet — but nothing here installs a scheduled job. If you later add one
  yourself with `crontab -e`, that is a deliberate, separate act, and you can
  remove it the same way.
- **Dry-run first.** The script is destructive in the sense that it moves
  files. Always preview with `--dry-run` before a real run so you can see
  exactly what will move and where — the single most important habit for any
  move-or-delete automation.
- **Scheduled jobs run unattended, so they must be safe and logged.** The
  reason this script is idempotent (safe to run twice) and writes
  `organize.log` (a record you can read the next morning) is precisely so it
  *could* be scheduled safely. Never schedule a script that lacks these
  properties, and never schedule one you have not read.
- **Quote everything; trust nothing.** The script quotes every path variable so
  a filename containing a space or special character cannot break a command
  apart. When you extend it, keep that discipline — unquoted variables in a job
  that runs on arbitrary filenames are a real hazard.
- **Privacy of logs.** `organize.log` records file names and timestamps, which
  are mildly revealing. It lives inside the folder you organized; keep it where
  only you can read it, and trim it if it grows.
