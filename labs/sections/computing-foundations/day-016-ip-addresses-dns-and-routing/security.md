# Security notes — Day 016 lab

- **What the scripts do:** they send DNS queries for a public test domain
  (`example.com`, reserved for documentation and testing) and a short
  `traceroute` toward it, then print and classify the results. They make **no
  other network connections**, write **no files**, and change **no settings**.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo` — installing the tools may, but running the lab does not. If any
  tutorial ever tells you to `sudo` a script you have not read, stop and read
  it first; this course reinforces that habit.
- **Privacy — the one thing to think about:** a `traceroute` reveals the path
  out of your network, which includes your ISP's routers and can indicate your
  rough geographic location and your provider. This is only mildly identifying
  (it does not expose your identity or credentials), but avoid pasting a full
  traceroute into a public forum without a glance at what it shows. Your DNS
  queries also travel to your resolver, which can log them — a reason some
  people choose a privacy-focused resolver or encrypted DNS, as the lesson
  discusses.
- **Only public, reserved targets:** the lab deliberately targets
  `example.com`, a domain the standards reserve for exactly this kind of
  testing, so you are never probing someone else's private systems. If you
  point the script at another host, use one you own or a well-known public
  site — running scans or traces against systems you do not control can
  violate acceptable-use policies.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is a common way developers get
  compromised; every lab script in this course is small enough to read and
  understand before executing.
