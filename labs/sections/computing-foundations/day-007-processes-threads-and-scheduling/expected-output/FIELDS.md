# Required output fields (all platforms)

A correct run of `process_playground.sh` prints, in order:

1. `=== Process Playground ===`
2. `Generated on: YYYY-MM-DD`
3. `Processes running right now: <positive integer>`
4. `This script's PID: <positive integer>`
5. A parent chain of one or more `pid ppid command` rows
6. `Started background worker: sleep 300 (PID <positive integer>)`
7. The worker in `jobs` output (`... Running ... sleep 300 &`)
8. The worker in `ps` output (a row with PID, PPID, STAT, and `sleep 300`;
   the worker's PPID equals the script's PID from line 4)
9. `Sent SIGTERM to <PID>; wait reported exit status 143 (143 = 128 + 15, death by SIGTERM)`
10. `Verified: PID <PID> is gone`
11. `=== End of playground ===`

`sample-run-macos.txt` in this directory is a real captured run (macOS,
Apple Silicon, 2026-07-12). **Every PID differs on every run** — PIDs are
assigned by the kernel at spawn time, so your numbers (and your process
count) will not match the sample, and that is expected. What must match is
the *shape*: the worker's PPID equals the script's PID, the exit status is
exactly 143, and the final verification line names the same PID that was
spawned. The parent chain also differs by how you launch the script: from
an interactive terminal it climbs through your shell and terminal app; the
sample was captured from a detached run, so its chain is short and ends at
the system's ancestral process (`/sbin/launchd` on macOS; on Linux you
would see `systemd` or `init` as PID 1). The `STAT` column may read `S` or
`SN` on macOS and `S` on Linux — both are the sleeping/waiting state.
