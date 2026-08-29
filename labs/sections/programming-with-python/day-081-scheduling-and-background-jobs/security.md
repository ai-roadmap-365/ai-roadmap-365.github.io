# Security and safety notes — Day 081

## The rule this lab is built around

**This lab installs nothing into any real scheduler, and leaves no process
running.** Not your crontab, not launchd, not systemd, not a stray background
python. A lesson that quietly schedules something on a learner's machine is
unacceptable — the learner would have no idea it existed, and it would keep
running long after the lesson was forgotten.

Concretely:

- `examples/gen_schedules.py` **writes text files** into a directory you name
  and prints the install commands. It never executes them.
- No file in `examples/` or `starter/` calls `crontab`, `launchctl` or
  `systemctl`. Section 8 of `tests/run_tests.sh` greps for exactly that and
  fails if it ever becomes untrue.
- Section 8 also reads (read-only) your real crontab, `~/Library/LaunchAgents`
  and `~/.config/systemd/user`, and asserts none of them contains this lab's
  job label.
- Every background process the suite starts is killed and waited for in a
  `trap ... EXIT`, and section 8 asserts that no `hold_lock.py`, `job.py` or
  `sleep` process survived.

If you decide later to schedule something for real, do it deliberately, on a
machine you own, having read the generated file first — and write down where
you put it.

## Scheduled jobs are a security surface

A scheduled job is a program that runs unattended, often with your privileges,
often for years. That deserves the same care as anything else that runs
without a person watching.

- **Least privilege.** Run the job as a dedicated user with access to exactly
  what it needs. A cron job running as root because that was easiest is a
  root shell waiting for a bug in your CSV parser.
- **The environment is not yours.** cron and launchd give a job a minimal
  environment. This is a safety feature, not an inconvenience: a job that
  works only because your shell profile exported a secret is a job that will
  break the moment somebody else installs it, and a job whose secret lives in
  a shell profile is a secret in the wrong place.
- **Secrets belong outside the schedule file.** A crontab line is world-
  readable on many systems and ends up in backups and screenshots. Read
  credentials from a file with restrictive permissions, or from a secret
  manager, and never from the command line — command lines are visible to
  every user in `ps`.
- **Writable schedule files are executable code.** Anything that can write
  your crontab, your `~/Library/LaunchAgents`, or a systemd unit directory can
  run arbitrary code as you, on a timer. Treat those paths as sensitive.
- **Log carefully.** The log line is written unattended and read later, often
  by more people than you expect. Log identifiers, counts and statuses; do not
  log credentials, tokens, personal data, or a whole request body "just in
  case".

## The locking and timeout code specifically

- `fcntl.flock` is an **advisory** lock: it stops cooperating programs, not a
  determined one. That is the right level for this problem — the thing you are
  defending against is your own job, started twice.
- The lock file's contents (a process id) are informational only. Never trust
  a pid from a file for anything that matters; pids are reused.
- `signal.setitimer` is cancelled in a `finally`. An alarm left armed fires
  later in an unrelated piece of code, which is a genuinely confusing bug.
- `supervise.py` uses `start_new_session=True` and `os.killpg` so a timeout
  kills the job's helpers too, then escalates SIGTERM to SIGKILL after a grace
  period. Without the process group, a killed job can leave grandchildren
  running for ever — which is exactly the failure this lab refuses to cause.

## No network, no keys, no accounts

Nothing here opens a socket. There is no API key, no account, no service to
sign up for, and no cost. `readings.csv` is a small file of invented
temperature readings; it contains no personal data.

## What the tests write

Everything is written into a directory created with `mktemp -d` or pytest's
`tmp_path`, and removed when the check or test finishes. The runner passes
`-p no:cacheprovider`, so pytest leaves no cache directory either. The only
files this lab adds to your working tree are the ones you create yourself in
`starter/`.
