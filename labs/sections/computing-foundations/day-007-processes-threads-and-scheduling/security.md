# Security notes — Day 007 lab

- **The iron rule: never signal a process you did not start.** Everything
  in this lab signals only the one `sleep` the script itself spawned, whose
  PID it captured from `$!` at the moment of creation. Typing `kill` with a
  PID you found lying around — in a tutorial, in old output, or by guessing
  — can terminate someone else's work or a system service. Before any
  manual `kill`, confirm with `ps -o pid,user,command -p <PID>` that the
  process is yours and is the one you think it is.
- **What the scripts do:** read the process table (`ps`), spawn one
  `sleep 300`, send it SIGTERM, and verify it exited. They make **no
  network connections**, write **no files**, and change **no settings**.
  The test suite only *reads* the process table; it never signals anything
  itself.
- **Privileges:** everything runs as your normal user, and that is itself a
  safety net — the kernel refuses to let you signal processes owned by
  other users. Nothing here needs `sudo`, and running `kill` with `sudo`
  removes that safety net; don't.
- **`kill -9` is a last resort, not a habit.** SIGKILL gives the target no
  chance to clean up — half-written files and stale locks are the typical
  wreckage. The lab teaches the professional order: SIGTERM, wait, then
  escalate only if truly necessary — and here the only target is ever a
  `sleep` you started seconds earlier.
- **PID reuse:** PIDs are recycled by the kernel. A PID you wrote down
  minutes ago may now belong to a different process — one more reason to
  capture `$!` immediately and act on it promptly, never on stale numbers.
- **Reading before running:** both scripts are short and commented — read
  them before executing, as with every lab in this course. A script that
  sends signals deserves an especially careful read.
