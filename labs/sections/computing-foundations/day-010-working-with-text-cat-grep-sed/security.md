# Security notes — Day 010 lab

- **What the scripts do:** read one small text file (`examples/samples/access.log`)
  and print counts to the console. They make **no network connections**, write
  **no files**, and change **no settings**. Every pipeline is read-only.
- **The sample data is synthetic.** The log is invented for this lab. Its IP
  addresses are drawn from the private ranges reserved by RFC 1918
  (`10.0.0.0/8` and `192.168.0.0/16`) — addresses that never appear on the
  public internet — and it contains no names, emails, cookies, or credentials.
  Nothing in it identifies a real person or machine.
- **Privileges:** everything runs as your normal user. No step needs `sudo`.
  If any tutorial ever tells you to `sudo` a script you have not read, stop and
  read it first — a habit this course reinforces.
- **Reading before running:** both scripts are short and commented. Read them
  before executing. Running unread shell scripts is a common way developers get
  compromised; every lab script here is small enough to read in full first.
- **Handling real logs later:** genuine web logs *do* contain personal data —
  IP addresses are often personal data under privacy law, and logs may hold
  session tokens or user IDs. When you apply these pipelines to real data,
  treat the log as sensitive: do not paste it into public forums, and strip or
  hash identifying fields before sharing.
