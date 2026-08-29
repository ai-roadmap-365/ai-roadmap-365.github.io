# Security notes — Day 097

## What this lab does to your machine

Almost nothing, and it is checked rather than promised.

- **No network.** Nothing here opens a socket. The test suite asserts that no
  file in `examples/` or `starter/` imports `socket`, `urllib`, `http` or
  `requests`, and that **no URL appears anywhere** in the lab's `.py`, `.sh` or
  `.toml` files at all.
- **No privilege.** Nothing runs `sudo`. The suite greps for a line that would
  actually invoke it, as opposed to a comment saying it does not.
- **No credentials.** There is no account, no key, no token, and no service to
  log in to.
- **No installation.** `requirements.txt` lists no packages.
- **No mess.** `tests/run_tests.sh`, `starter/03_check.sh` and
  `examples/05_dictconfig_and_rotation.py` each build everything inside
  `mktemp -d` and remove it in a `trap` or a `finally`. The suite asserts
  afterwards that no `app.log`, no `daily.log` and no `__pycache__` was left in
  the lab directory.

## The key in this lab is invented

The string `sk-live-9f2c4a7b1e63` appears throughout — in `examples/01_prints.py`
where it is deliberately printed, in the redaction demonstrations, and in the
test suite where its **absence** is asserted.

It is invented for this lab. It has never been a credential, it authorises
nothing, and it exists only so that the tests can look for it in real captured
output and fail if they find it.

If you replace it, replace it with something equally obviously fake. A lab that
teaches secret hygiene using a plausible-looking key is a lab that will
eventually put a plausible-looking key into somebody's screenshot.

## A secret in a log line is an incident

This is the day's own security point, and the reason it is stated this
strongly: **a log is the most-copied artifact a running system produces.**

Within minutes of anything going wrong, a log excerpt is in a ticket, in a
chat message, in a screenshot, in a CI artifact, and in three people's
terminal scrollback. A credential that reached the log has therefore reached
all of those places, and every one of them has to be found before the rotation
is complete. That is why it is an incident with a checklist rather than a lint
failure with a fix.

Four rules, in order of how much they buy you:

1. **Do not log the secret.** Everything else on this list is a backstop for
   the moment somebody does it anyway.
2. **Do not put a secret in an exception message.** The lab measures why: a
   redacting filter does not touch the traceback, because the traceback is
   rendered by the formatter after every filter has already run. A secret
   inside `RuntimeError(f"rejected key {key}")` walks straight past the filter.
   Raise `RuntimeError("upstream rejected the credential")` instead — the
   traceback still tells you where, and it tells nobody what.
3. **Redact by value, on every handler.** `RedactingFilter` in
   `examples/applog.py` replaces known secret values wherever they appear —
   message, arguments, `extra=` fields, values nested inside a dict. Attach it
   to each handler, for the reason in the next section.
4. **Scrub in the formatter too, if you can afford it.** A formatter that
   redacts its finished line catches the traceback case as well. It costs one
   substring search per known secret per line.

The honest limits of value redaction, all three of them real:

- It only knows the values you hand it. A secret it has never been told about
  goes through untouched.
- It cannot see a transformed secret — base64-encoded, truncated to a prefix,
  or split across two log calls.
- Very short values are ignored, because redacting every occurrence of a
  four-character string would destroy the log.

## Where the filter goes, and why the obvious answer is wrong

Measured in this lab, and asserted by the test suite so that a future Python
changing it would fail the build:

**A filter attached to a logger runs only for records logged through that
logger object.** Records arriving by propagation from a descendant logger skip
every ancestor's filters — propagation walks the ancestors' *handlers*, not
their *filters*.

So this looks like whole-application protection and is not:

```python
logging.getLogger("myapp").addFilter(RedactingFilter([api_key]))
```

Every module that does the right thing and calls `logging.getLogger(__name__)`
is a descendant of `myapp`, so every one of them bypasses that filter. The lab
prints both lines side by side: the record logged directly on `myapp` is
redacted; the record logged on `myapp.loader` is not.

Attach redaction to each **handler**. A handler sees everything that reaches
its destination, from anywhere in the tree. In `dictConfig` that is a
`"filters": ["redact"]` entry on each handler, which is what
`examples/05_dictconfig_and_rotation.py` does.

## Secrets belong in the environment, never in the repository, never in a flag

`examples/config.toml` is the shared configuration file and it contains **no
secret**, deliberately. A secret in a file in a repository is a secret in
every clone, on every laptop, in every backup, and in the history forever —
including after somebody deletes the line, which does not remove it from the
history.

The `api_key` setting in `examples/appconfig.py` also has **no command-line
flag**, and that is a security decision rather than an oversight:

- A value on the command line is visible in `ps` to every other user on the
  machine.
- It lands in the shell history file, in plain text, indefinitely.
- It appears in the process arguments a supervisor or container runtime
  records.

Environment variable, or a secret manager that injects one. For anything
beyond a single machine, prefer the secret manager: it gives you rotation,
access logs and expiry, none of which an environment variable has.

## What the provenance table is allowed to say

`Config.provenance_table()` prints every setting with its value and its
source, and for a secret it prints `***redacted***` in the value column while
still printing the source. That split is deliberate, and it is the useful one.

"Is the key set, and did it come from the environment or from the file?" is an
operational question you need answered at 3 a.m. "What is the key?" is never a
question a log or a console needs to answer. The first is safe; the second is
the incident.

The same rule runs through the validation messages: a problem with a secret
setting names the setting and says `***redacted***`, never the value.

## Configuration is an attack surface too

Three points that are easy to miss because configuration feels inert.

**Precedence is a privilege question.** The flag layer wins here, which is
correct for a program a person runs. For a service, a flag that can override a
deployment's security-relevant settings — an authentication toggle, a target
host, a verification flag — is a way to weaken the service from the command
line. Decide deliberately which settings may be overridden from which layer.

**A configuration file is code you did not review.** `tomllib` is a parser for
a data format with no execution semantics, which is exactly why it is used
here rather than something that evaluates. Never configure a program by
importing a Python file, or by `eval`-ing a string, however convenient it
looks: that is arbitrary code execution with extra steps.

**Validate before you act, not while you act.** A configuration value that is
only checked at the moment it is used gives an attacker or an accident the
whole program's startup to work with. `validate_or_die` runs before anything
happens and exits with status 2 — the lab asserts that exit code, and asserts
that the message names both the setting and the layer it came from.

## Cleanup

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Nothing else was created, nothing was installed, and nothing outside this
directory was touched.
