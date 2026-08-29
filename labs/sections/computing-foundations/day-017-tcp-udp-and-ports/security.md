# Security notes — Day 017 lab

- **What the scripts do:** read the local list of listening TCP sockets
  (`lsof` / `ss` / `netstat`) and print it, then make one or two
  connectivity probes to the **loopback address `127.0.0.1`** with `nc -z`
  (no data is sent). They write **no files**, change **no settings**, and
  make **no connection to any external host**.
- **Loopback only — never scan others.** The `-z` probes only ever target
  `127.0.0.1` (this machine talking to itself). Pointing a port scanner at
  machines you do not own is, in many jurisdictions, unauthorised access —
  it can be a crime and will get you banned from most networks. This lab
  hard-codes the loopback so you cannot do it by accident, and the test suite
  fails if any `nc` probe uses a non-loopback address.
- **Privileges:** everything runs as your normal user. Nothing needs `sudo`.
  Without `sudo`, `lsof` shows fewer entries — that is a feature, not a
  problem. If a tutorial ever tells you to `sudo` a script you have not read,
  stop and read it first.
- **Privacy:** the list of listening ports and process names is mildly
  revealing (it shows what software you run and its patch surface). Sharing
  it in a class forum is normally fine; avoid posting the full listing of an
  employer-managed machine.
- **Reading before running:** both scripts are short and commented. Reading a
  script before you run it is the single best habit for staying safe on the
  command line, and this course reinforces it every day.
