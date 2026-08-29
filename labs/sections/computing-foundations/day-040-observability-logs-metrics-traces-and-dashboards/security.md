# Security notes — Day 040 lab

- **What the scripts do:** generate synthetic log lines in a temporary file,
  compute metrics from them, and print a dashboard and a trace. They make **no
  network connections**, need **no elevated privileges**, and write only to a
  temporary file that is **removed automatically on exit** (via a `trap`).

- **Logs can leak secrets and personal data — the central lesson.** In the real
  world, logs are one of the most common places credentials and personal
  information leak: a careless line that records a full request can capture a
  password, an API key, a session token, or a user's personal details in plain
  text, and that log may then be shipped to a third-party service and retained
  for a long time. **Never log credentials, tokens, or full request bodies
  without scrubbing them first.** Treat logs as sensitive data.

- **This lab logs only synthetic data.** Every value the scripts emit is made
  up — fixed timestamps, fake request ids, and computed latencies. Nothing about
  your machine, your accounts, or any real person is collected or written. This
  is deliberate: it lets you practice the mechanics of logging without ever
  handling sensitive data.

- **Privacy in practice:** because real logs and traces record real user
  activity, they often fall under privacy regulations and data-retention rules.
  Responsible instrumentation logs identifiers rather than raw personal data
  where possible, sets retention limits, and can delete a user's records on
  request. Keep this in mind the first time you point logging at a real service.

- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is a common way developers get
  compromised; every script in this course is small enough to read before you
  run it.
