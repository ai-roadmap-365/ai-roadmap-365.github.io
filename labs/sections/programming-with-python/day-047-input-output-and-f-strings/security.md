# Security notes — Day 047 lab

- **Never `eval()` input.** The most dangerous mistake with `input()` (or with
  `sys.argv`, or with piped data) is passing it to `eval()`, which executes the
  text as Python code. `eval(input())` lets whoever supplies the input run any
  command on your machine — delete files, open a network connection, anything.
  This lab deliberately turns text into numbers with `float()`, which parses a
  value and nothing more. Whenever you need a number from input, reach for
  `int()` or `float()`, never `eval()`.

- **Validate and convert every input.** Input is data, not instructions. The
  program checks that it received exactly two whitespace-separated tokens and
  that both convert to numbers, and it rejects anything else with a clear error.
  Treating all input as untrusted until validated is the habit behind every
  defense against injection attacks.

- **Mind what you print, and where.** Output is where data leaves your program.
  Printing a secret for debugging is the classic way a password or key leaks
  into a terminal, a log, or a screen-share. Standard error is captured by
  logging systems just as readily as standard output, so "I only printed it to
  stderr" is no protection. Before every `print()`, consider who can see that
  channel.

- **What these scripts do:** read a pair of numbers, compute a few statistics,
  and print them. They make **no network connections**, write **no files**, and
  change **no settings**. They need no elevated privileges — nothing here should
  ever require `sudo`.

- **Read before you run.** Both `io_demo.py` files are short and commented; read
  them before executing. Running unread scripts is one of the most common ways
  developers get compromised, and this course's rule is that every lab file is
  small enough to read and understand first.
