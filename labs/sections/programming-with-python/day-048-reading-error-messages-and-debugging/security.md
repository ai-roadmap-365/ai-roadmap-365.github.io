# Security notes — Day 048 lab

- **Never run untrusted `.py` files.** A Python program can do anything your
  user account can do — read and delete files, make network connections,
  install software. Running a script you have not read is one of the most
  common ways developers get compromised. The rule this course follows: every
  script in a lab is small enough to open and read before you run it. Do the
  same with any code you find elsewhere.
- **These samples are safe and local.** The six programs here are a few lines
  each. They only build small lists and dictionaries, do arithmetic, and print
  text. They read **no input**, open **no files**, make **no network calls**,
  and need **no elevated privileges**. Open them and confirm this for yourself —
  that habit is the point.
- **The shell scripts are equally small.** `debug_walkthrough.sh` and
  `run_tests.sh` only run the sample programs and read their output. They write
  nothing outside their own console output (aside from a temporary file the
  test cleans up) and touch no network.
- **Tracebacks can leak information.** A real traceback shows file paths and
  internal details. That is fine on your own machine, but when you build
  programs for others, do not display raw tracebacks to users — log them
  privately instead, as the lesson explains. The captures in this lab use
  relative paths so they carry no personal information.
