# Scheduling the organizer with cron — read, understand, opt in later

This file shows how you *would* run `organize_files.sh` on a schedule. You do
**not** have to install any of these, and this lab never edits your crontab for
you. Read the examples to understand the syntax; if and when you want a real
scheduled job, you add it yourself, deliberately, with `crontab -e`.

## The shape of a crontab line

```text
┌── minute (0–59)
│ ┌── hour (0–23)
│ │ ┌── day of month (1–31)
│ │ │ ┌── month (1–12)
│ │ │ │ ┌── day of week (0–7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *   command to run
```

Always use **absolute paths** in a crontab line: cron runs with a bare
environment and an unpredictable working directory, so `~/Downloads` or a
relative script path may not resolve. Spell everything out.

## Ready-to-read examples

Organize your Downloads folder **every day at 8:00 p.m.**:

```text
0 20 * * * /usr/bin/env bash /Users/you/labs/.../examples/organize_files.sh "$HOME/Downloads"
```

Organize it **every Monday at 6:00 a.m.**:

```text
0 6 * * 1 /usr/bin/env bash /Users/you/labs/.../examples/organize_files.sh "$HOME/Downloads"
```

Organize it **every 15 minutes during weekday business hours** (a busy shared
folder):

```text
*/15 9-17 * * 1-5 /usr/bin/env bash /path/to/organize_files.sh "$HOME/Inbox"
```

Preview instead of acting — a **daily dry run** whose output you can inspect,
useful while you still don't fully trust a job:

```text
0 20 * * * /usr/bin/env bash /path/to/organize_files.sh --dry-run "$HOME/Downloads" >> "$HOME/organize-dryrun.log" 2>&1
```

The trailing `>> file 2>&1` sends both normal output and errors to a log file
you own, which is exactly how unattended jobs keep a record you can read the
next morning.

## How to add one yourself (only if you choose to)

```bash
crontab -l          # list your current jobs (may be empty — that is normal)
crontab -e          # open your crontab in an editor; add ONE line; save; quit
crontab -l          # confirm the line is there
```

To remove it later, run `crontab -e` again and delete the line. On macOS the
modern, recommended scheduler is `launchd` rather than cron; on Linux you may
prefer a `systemd` timer. The five-field idea above is the same in all of
them — learn it once, read them all.

## Safety reminder

Only ever schedule a script you have **read**, that supports **--dry-run**, and
that **logs** what it does. Run it by hand (and in dry-run) several times first.
A scheduled job runs faithfully, unattended, for as long as you leave it in the
table — make sure it is a job you trust that much.
