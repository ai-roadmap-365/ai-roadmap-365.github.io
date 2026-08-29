# Schedule files — shown, never installed

Everything in this directory is a **reference**. Nothing here is installed by
this lab, and nothing here is executed by the test suite. That is the same
safety rule Day 81 followed: a course must not write into your real `crontab`,
your `~/Library/LaunchAgents`, or your systemd user units, and it must not
leave a background process running when you close the terminal.

To try one of these for real on your own machine, read it first, change the
paths to yours, and install it yourself with the command noted at the top of
the file. To undo it, use the removal command noted at the bottom.

| File | Supervisor | Platform |
| --- | --- | --- |
| `feedkit.cron` | `cron` | macOS, Linux, anything Unix-like |
| `com.example.feedkit.plist` | `launchd` | macOS |
| `feedkit.service` + `feedkit.timer` | systemd | most Linux distributions |

## The three things every one of them gets right

**An absolute path to the executable.** A scheduler does not run your shell
profile, so `PATH` is nearly empty and `feedkit` will not be found. Write
`/home/you/.local/bin/feedkit`, or the path inside your virtual environment.
This is the single most common reason a job that works by hand does nothing on
a schedule.

**A working directory, set explicitly.** `state_file = "feedkit-state.json"`
is relative to wherever the job starts, and where a job starts differs between
cron, launchd and systemd. Either set the working directory in the schedule
file or use an absolute `state_file` — the examples do both, belt and braces.

**The environment, supplied explicitly.** `FEEDKIT_BASE_URL` and
`FEEDKIT_TOKEN` are not in your shell profile as far as the scheduler is
concerned. Each file below shows where its supervisor expects them, and each
one keeps the token in a file that only you can read rather than in the
schedule entry itself.

## The fourth thing, which none of them can do for you

None of these supervisors will tell you that the job **stopped running**. cron
mails output when there is output; launchd and systemd record exits. All three
are silent about a job that was never triggered at all — because the plist was
unloaded, the timer was masked, the laptop was shut, or the crontab was lost
with the machine. That is what `feedkit status --max-age-minutes` is for, and
why the watchdog belongs somewhere other than the thing it is watching.
