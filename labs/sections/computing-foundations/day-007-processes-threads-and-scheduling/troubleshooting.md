# Troubleshooting — Day 007 lab

## `kill: (12345) - No such process`

The PID is stale or mistyped. `sleep 300` exits on its own after five
minutes, and every run gets fresh PIDs — never reuse a PID from an earlier
run or from the sample output. Start a new sleeper and capture `$!`
immediately: `sleep 300 & worker_pid=$!`.

## `wait: pid 12345 is not a child of this shell`

`wait` only collects children of the shell you call it from. If you started
the sleeper in one terminal and typed `wait` in another (or inside a script,
which is its own shell), it is not your child there. Run the whole
lifecycle — spawn, observe, kill, wait — in one shell, start to finish.

## `jobs` prints nothing even though my sleep is running

`jobs` is per-shell: it lists only the background jobs of the shell you
type it in. Your sleeper still exists — find it system-wide with
`ps -p <PID>`. Same rule as above: one terminal for the whole exercise.

## Orphaned sleeps: I started sleepers and lost track of them

It happens — a closed terminal or a script that died before its cleanup.
First, *look*: `pgrep -l sleep` lists every `sleep` process you can see,
with PIDs. Identify the ones **you** started (on a shared machine, other
users and system tools may legitimately run sleeps — check ownership with
`ps -o pid,user,command -p <PID>`), then terminate only those, politely:
`kill <PID>`. An orphaned `sleep 300` is harmless — it uses no CPU and
exits by itself within five minutes — so when in doubt, just wait it out.
Both lab scripts set a `trap ... EXIT` so their own worker is taken down
even if the script fails partway; that pattern is worth stealing.

## The starter script says "Exercise 3 not completed yet"

Working as designed: the spawn/kill/verify steps only run after you replace
`worker_pid="unknown"` with a real spawn (`sleep 300 &` then
`worker_pid=$!` on the next line, inside the script).

## Exit status is 0, not 143

Your `wait` collected the wrong thing, or the sleeper finished naturally
before you killed it (five minutes pass quickly when reading). Rerun and
kill promptly. If you see 137 instead of 143, you sent SIGKILL (`kill -9`)
rather than SIGTERM — reread the lesson's signals table.

## `ps: illegal option` or missing columns

Use the exact portable form `ps -o pid,ppid,stat,command -p <PID>`. Other
spellings (`ps aux` variants, `--forest`) differ between macOS and Linux.

## My parent chain looks different from the sample

Expected. The sample was captured from a detached run, so its chain ends at
`/sbin/launchd`. Run from a normal terminal and you will see your shell,
your terminal app or editor, and eventually PID 1. That difference *is* the
lesson: every process has a parent, and the chain depends on who spawned
whom.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu). Native PowerShell has its own
process cmdlets (`Get-Process`, `Stop-Process`), but this lab's scripts and
tests assume a Unix-style shell.
