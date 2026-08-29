# Security notes — Day 038 lab

- **What the scripts do:** read one committed, synthetic sample file
  (`examples/samples/data.txt`) and print matches and counts to your terminal.
  They make **no network connections**, write **no files** (except the tests you
  choose to redirect), and change **no settings**.
- **The sample is fictional.** Every name, email, phone number, and IP address
  in the sample is invented for practice (`example.com`/`.org`/`.net` are
  reserved documentation domains; the IPs are private-range). Nothing in this
  lab touches real personal data.
- **Never `eval` matched text.** A recurring real-world danger with regex is
  taking text a pattern extracted and executing it as a command
  (`eval "$match"`) or interpolating it into a shell command. Matched text is
  *untrusted input*; treat it as data, never as code. This lab only prints
  matches — it never runs them — and you should keep that habit.
- **Watch for catastrophic backtracking (ReDoS).** If you later run patterns
  over untrusted input, avoid nested quantifiers over overlapping classes (the
  classic `(a+)+$` shape), prefer specific classes like `[^"]*` to broad `.*`,
  and use tools or engines with a timeout. A single crafted input can otherwise
  freeze a process.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`; if any tutorial asks you to `sudo` a script you have not read, stop
  and read it first.
