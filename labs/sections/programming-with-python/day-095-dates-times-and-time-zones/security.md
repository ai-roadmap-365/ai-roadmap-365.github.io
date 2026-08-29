# Security notes — Day 095

## What this lab does to your machine

Almost nothing, and the test suite checks each claim rather than promising it.

- **No network.** Nothing here opens a socket. The suite asserts that no file
  in `examples/` or `starter/` imports `socket`, `urllib`, `http`, `requests`,
  `ftplib` or `smtplib`, and that **no URL appears anywhere** in the lab's
  `.py` or `.sh` files at all.
- **No privilege.** Nothing runs `sudo`, and the suite greps for a line that
  would actually invoke it rather than a comment saying it does not. In
  particular, nothing in this lab changes your system clock or your system
  time zone — both would need root, and a lab that moved your clock would be
  a rude thing to run. Every "what if the clock jumped" demonstration computes
  the answer from real transition data instead.
- **No credentials.** There is no account, no key, no token and no service.
- **No installation.** `requirements.txt` lists no packages. The one exception
  is Windows, where `zoneinfo` needs the `tzdata` package because Windows
  ships no IANA database; that is documented in `requirements/README.md` and
  is not required for the macOS or Linux path.
- **No mess.** The suite works inside `mktemp -d` and removes it in a `trap`,
  `PYTHONDONTWRITEBYTECODE=1` is exported so no `__pycache__` appears, and the
  suite asserts afterwards that no `__pycache__` and no stray file was left in
  the lab directory.

## The data in this lab

There is none. No personal data of any kind appears here: no names, no email
addresses, no records. The only data are calendar instants — public facts
about when governments moved their clocks — and four invented order events
labelled "ordered", "packed", "dispatch" and "checkout".

## Timestamps are personal data more often than people expect

This is the day's own security point, and it is worth stating plainly because
timestamps do not feel like personal data.

**A precise timestamp plus a local time zone is a location signal.** Storing
`Europe/London` next to a user's activity says roughly where that person is,
and a change in that field says they moved. Storing UTC instants and rendering
in the viewer's zone at display time gives you the same product with none of
that inference stored.

**A sequence of timestamps is a behavioural profile.** When somebody logs in,
how long they stay, whether they work at 02:00 — none of that is anybody's
name and all of it identifies a person quite well. Timestamps at
microsecond precision are also a strong fingerprint for correlating one
person's records across two systems that share nothing else.

**Precision is a decision.** If your feature needs "which day did this
happen", storing the second and the microsecond is data you have chosen to
hold and must now protect, retain and delete correctly. Round at the point of
collection; you cannot un-collect later.

## The security-relevant failures that time causes

Three of these are real classes of vulnerability rather than merely bugs, and
all three are the direct consequence of what this lab teaches.

**Expiry checks that use the wall clock.** A token that expires "one hour from
now" evaluated against `time.time()` can be handed an extra hour of validity
by a clock adjustment, and a session that should have ended can be extended by
moving the clock. Durations belong on a monotonic clock; absolute expiry
belongs on a UTC instant that no local rule can move.

**Signature and certificate windows.** "Valid from" and "valid until" are
absolute instants. Comparing them against a naive local datetime means the
comparison is off by the offset — an hour or several — and in the wrong
direction it accepts something that has expired. Compare aware instants, in
UTC, always.

**Retries and lockouts.** "Three failed attempts in five minutes" measured
with a wall clock can be reset by a clock jump, and on the 25 October night
the five-minute window genuinely covers sixty-five minutes of real time.

## Two smaller sharp edges

**`datetime.utcnow()` is deprecated, and it was always a trap.** It returns a
*naive* datetime holding UTC field values, so it looks exactly like a local
time and compares wrongly against one with no error raised. Write
`datetime.now(timezone.utc)` and get an aware value that cannot be
accidentally compared to a local one.

**Parsing untrusted timestamps.** `datetime.fromisoformat` and
`strptime` raise `ValueError` on rubbish, which is the correct behaviour and
also means an unhandled one is a denial of service on a request handler. Catch
it. And prefer `fromisoformat` over hand-rolled parsing: a regular expression
over date text is one of the more reliable ways to write a
catastrophically backtracking pattern.

## Cleanup

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Nothing else was created, nothing was installed, and nothing outside this
directory was touched. If you only ran the two shell scripts, there is nothing
to clean up at all — they set `PYTHONDONTWRITEBYTECODE=1`, work in a temporary
directory, and the suite asserts that the lab directory is unchanged
afterwards.
