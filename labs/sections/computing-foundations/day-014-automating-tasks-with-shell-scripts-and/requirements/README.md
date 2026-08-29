# Dependencies — Day 014 lab

**None beyond a POSIX shell.** This lab has zero installable dependencies:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- Standard OS utilities only: `basename`, `dirname`, `mkdir`, `mv`, `tr`,
  `date`, `find` — all part of the base system.

There is deliberately no `requirements.txt` / `package.json` here: the lab runs
on a factory-fresh machine with nothing installed.

No scheduler is required or configured. The lab **reads about** cron, launchd,
systemd timers, and Task Scheduler but installs none of them and never edits
your crontab. If you later choose to schedule the script yourself, `crontab`
(part of cron) already ships with macOS and Linux — but that is optional and
outside the tested lab.
