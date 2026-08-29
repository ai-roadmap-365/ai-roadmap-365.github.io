# Security notes — Day 002 lab

- **What the scripts do:** `examples/toy_cpu.sh` reads a text file you
  name on the command line, simulates four arithmetic-and-print
  instructions, and writes only to your terminal. `tests/run_tests.sh`
  runs the simulator on the bundled programs plus a few deliberately
  broken ones it creates in a temporary directory (removed on exit).
  Neither script makes **any network connections**, writes files into the
  repository, or changes settings.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`, and nothing ever will for this lab.
- **Interpreting untrusted programs:** the simulator validates every
  instruction against a four-opcode whitelist and rejects anything else
  with a non-zero exit code — it never passes program text to the shell
  for execution. Still, treat program files from other people the way you
  treat any file from the internet: read them first. They are at most
  seven lines long.
- **Reading before running:** the simulator is about 180 commented lines —
  short enough to read end to end, and the lab expects you to. Running
  unread shell scripts is one of the most common ways developers get
  compromised; every lab in this course keeps its scripts small enough to
  audit before executing, and this one doubles as the lesson itself.
