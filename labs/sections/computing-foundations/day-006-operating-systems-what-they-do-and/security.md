# Security notes — Day 006 lab

- **What the scripts do:** read information the OS already publishes
  (`uname`, `uptime`, `whoami`, `df`, `ps`, and a read-only `ls` of the
  kernel file) and print it. They make **no network connections**, write
  **no files**, change **no settings**, and are strictly read-only.
- **Privileges:** everything runs as your normal user. Nothing in this lab
  needs `sudo` — and today's lesson explains exactly why that matters: the
  kernel/user-space boundary is the machine's security foundation, and
  `sudo` asks the OS to suspend it. If any instruction ever tells you to
  `sudo` a script you haven't read, stop and read it first.
- **Privacy — `ps` sees a lot:** on a shared or multi-user machine,
  `ps aux` lists *other users'* processes too, including their full command
  lines. Command lines sometimes contain sensitive material (file names,
  server addresses, and — a classic mistake — passwords passed as
  arguments). Two habits follow: never put secrets on a command line, and
  treat process listings from shared machines as confidential.
- **Sharing your output:** an OS profile (kernel version, uptime, process
  names) reveals your patch level and the software you run — useful to an
  attacker profiling a target. Sharing it in a class forum is normally
  fine; avoid posting profiles of employer-managed machines, and skim the
  process list for anything personal before pasting.
- **Reading before running:** both scripts are short and commented — read
  them first. Running unread shell scripts is one of the most common ways
  developers get compromised; every lab script in this course is small
  enough to read and understand before executing.
