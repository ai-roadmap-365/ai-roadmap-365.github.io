# Security notes

This lab handles a credential, writes files, and describes running unattended
on a schedule. Each of those has a specific thing to get right.

## The secret

The toolkit reads its access token from `FEEDKIT_TOKEN` in the environment. It
reads it from nowhere else — not from the configuration file, not from a
command-line flag, not from a file in the project. Three reasons, in order of
how often they bite people:

1. **A flag ends up in your shell history and in `ps` output.** Anyone who can
   list processes on the machine can read a token passed as an argument.
2. **A configuration file ends up in version control.** Not on purpose; on the
   day somebody runs `git add -A` in a hurry. Once it is in the history it is
   in every clone, every fork, and every backup, and removing it means
   rewriting history and rotating the credential anyway.
3. **The environment is where deployment tooling already puts secrets.**
   systemd's `EnvironmentFile`, a mode-600 file sourced by a wrapper, a
   keychain lookup — all of them hand the value over the same way.

The lab proves this rather than asserting it. `tests/run_tests.sh` invents a
token, the fixture server **requires** it (every request without it is refused
with 401, which the suite checks), and then the suite greps the captured log,
the state file and the `--explain-config` output for that exact string and
demands zero matches.

### Redaction is a seatbelt, not a licence

`logging_setup.RedactingFilter` replaces known secret values anywhere they
appear in a log record — in the message, in the arguments, in the structured
fields, and in an exception's own text. It exists because one day somebody will
log a whole response object, or an error message that quotes a URL with a token
in the query string.

It is not a substitute for not logging credentials. It only knows about secrets
it was told about, it cannot redact a token that arrives in a shape it does not
recognise, and a value shorter than six characters is ignored deliberately
(redacting a three-character "secret" would blank half the alphabet).

### If a token leaks

In this order, and the order matters:

1. **Revoke it at the provider.** Before anything else. A leaked credential
   that still works is the only part of this that is an emergency.
2. **Issue a replacement** and put it wherever the running job reads from.
3. **Assume it was used.** Read the provider's access logs for the period
   between the leak and the revocation.
4. **Only then** clean up the leak itself — the log file, the commit, the
   screenshot. Scrubbing first and revoking second gets the priority exactly
   backwards, and rewriting a repository's history does not un-publish anything
   that was already cloned.
5. **Fix the path that leaked it**, so the next one does not go the same way.

## The files this lab writes

Everything is written under the working directory or a temporary directory
created by `mktemp -d`:

- `feedkit-state.json` — the record of what has been processed. No credentials,
  no personal data: entry ids, titles and timestamps from the fixture files.
- `feedkit-state.json.lock` — a lock file containing a process id, created with
  mode `0600`.
- Temporary files named `feedkit-state.json.*.tmp`, which exist for
  milliseconds during an atomic write and are removed on any failure.

Nothing is written outside the lab directory and the system temporary
directory. Nothing needs `sudo`. `.venv/` is a build product and is ignored by
version control.

## The network

The install is the only step that reaches the internet. **The tests do not.**
The fixture server binds `127.0.0.1` on a port the operating system chooses,
and the suite asserts that no source file in the lab names any host other than
`127.0.0.1`.

That is a safety property as much as a speed one: a lab that quietly issued
requests to a third-party site would be teaching every learner who ran it to
send traffic somebody else has to pay for.

## The scheduler

**Nothing in this lab is installed into cron, launchd or systemd.** The files
under `examples/schedule/` are references: each one carries `NOT INSTALLED BY
THIS LAB` at the top, the install and removal commands, and the note that every
path in it must be changed. The suite asserts that no Python file in the lab
imports `subprocess` or calls `os.system`, so there is no code path that could
reach a scheduler even by accident.

If you do adopt one of them on your own machine:

- The systemd unit shows modest hardening — `ProtectSystem=strict`,
  `ProtectHome=read-only`, `NoNewPrivileges=true`, and an explicit
  `ReadWritePaths` for the one directory the job writes to. None of it is
  exotic and all of it is free.
- Keep the token in an `EnvironmentFile` with mode 600, not in an
  `Environment=` line: `systemctl show` prints those.
- A crontab entry is readable by more people than you expect on a shared
  machine, and ends up in backups. Source a mode-600 file instead.
- Run the job as your own user, never as root. Nothing here needs privilege,
  and a scheduled job with more privilege than it needs is a standing invitation.

## What this lab does not protect against

Being explicit about the limits is part of the point:

- **The fixture server has no security properties worth the name.** It is a
  test double. It serves only 127.0.0.1, refuses paths outside its fixture
  directory, and is not fit for anything else.
- **The lock is single-machine.** `O_CREAT | O_EXCL` on a local filesystem is
  reliable; over a network filesystem it is not, and this is not a distributed
  lock.
- **The toolkit trusts what its sources return**, beyond validating the shape.
  It never executes anything from a payload, but a real toolkit that renders
  fetched titles into HTML or shells out with fetched values would need a great
  deal more care than is shown here.
