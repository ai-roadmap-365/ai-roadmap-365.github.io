# Security notes — Day 096

## What this lab does to your machine

| Action | Does this lab do it? | Evidence |
| --- | --- | --- |
| Reach the internet | No | `requires_network: false`. The suite asserts no URL in any file names a host other than the loopback address |
| Open a listening socket | Yes — on `127.0.0.1` only | `examples/labkit.py` binds `("127.0.0.1", 0)`; the suite asserts that literal is present |
| Run `sudo` | No | The suite scans every `.py` and `.sh` file for a line that would invoke it |
| Install anything | No | `requirements/requirements.txt` lists no packages; the suite parses every import and fails on any non-standard-library name |
| Need a credential or key | No | `requires_api_key: false`. Nothing here authenticates to anything |
| Write outside its own directory | No | Everything goes into `mktemp -d`, removed in a `trap` |
| Leave files behind | No | `PYTHONDONTWRITEBYTECODE=1` is set by both harness scripts, and the suite asserts no `__pycache__` survives |
| Start processes | Yes — its own worker processes | `ProcessPoolExecutor` with a bounded pool, shut down by its `with` block |
| Change process-wide interpreter state | Yes — briefly | `sys.setswitchinterval`, always restored in a `finally`; the suite verifies the restoration |

These are checks the suite performs, not promises this file makes. Run
`bash tests/run_tests.sh` and read section 8 of its output.

## The fixture server

The only network activity in this lab is a small HTTP server that
`examples/labkit.py` starts, uses and shuts down inside a context manager.

- It binds to **`127.0.0.1`**, the loopback address, so it is reachable only
  from your own machine. It is not exposed on your local network, and a
  firewall prompt is not expected.
- It binds to **port 0**, which asks the operating system for a free
  ephemeral port. It therefore cannot collide with a service you are already
  running, and two copies of this lab can run at the same time.
- It answers every path identically, after a sleep. It reads nothing from
  disk, executes nothing, and stores nothing. There is no path handling to
  get wrong, and therefore no directory-traversal surface.
- It is shut down and closed in a `finally` block, and its thread is joined,
  so no socket is left listening after the script exits.
- Its per-request log line is suppressed, which is a readability decision
  rather than a security one, and is stated in the code.

`http.server` is documented by Python as **not recommended for production**
because it implements only basic security checks. That is the correct use of
it here — a disposable fixture on the loopback address for the duration of
one script — and it is the reason this lab does not suggest exposing it.

## `sys.setswitchinterval` is process-wide

`examples/04_race.py` and `starter/_progress.py` both lower the interpreter's
thread switch interval to 1 microsecond in order to make a latent race
land reliably. This is a global setting, not a scoped one.

Both restore the previous value in a `finally` block, so an exception cannot
leave your interpreter in that state, and `tests/run_tests.sh` asserts that
the value is unchanged after the race function has run. If you copy this
technique into your own diagnostics, copy the `finally` with it: leaving an
interpreter at a 1 microsecond switch interval makes every threaded program
in that process dramatically slower.

## Concurrency as a security surface

This is the part specific to today, and it is worth more than the checklist
above.

**A race condition is a security bug, not only a correctness bug.** The lost
update in `examples/04_race.py` is a toy: two threads read a counter, both
add one, one write wins, one increment vanishes. Replace "counter" with
"account balance", "remaining quota", "number of licences in use" or "has
this token already been redeemed?", and the same shape becomes a
time-of-check-to-time-of-use flaw. The pattern to recognise is any sequence
of *check, then act* where the state can change in between:

```text
if user.has_permission(document):   # the check
    send(document)                  # the act — permission may have been revoked
```

The lab's own demonstration is the honest version of why this class of bug is
so dangerous: on the authoring machine the unprotected counter lost nothing
at all in 20 trials at the default settings, and lost 70% of its increments
when the thread switch interval changed. **The bug was equally present in
both cases.** Only its visibility changed. You cannot test your way to
confidence here; you either reason about the invariant, or you remove the
shared mutable state.

**A blocked event loop is a denial of service you inflict on yourself.**
`examples/03_blocking_coroutine.py` measures an unrelated task being starved
for 211 milliseconds by one coroutine that called `time.sleep`. In a real
service that is one slow synchronous call in one request handler stopping
every other request on that worker. No error is raised, no alert fires, and
the metric that shows it is tail latency rather than an error rate. An
attacker who finds the one endpoint that blocks does not need a botnet.

**Timeouts are not optional on anything that waits.** `examples/06_timeouts.py`
shows a request cancelled at the caller's budget rather than the work's
length. Without one, a slow or hostile upstream decides how long your service
holds a connection, a thread, or a slot in a pool. Note that cancellation in
asyncio is an exception delivered inside the task, so `finally` blocks run and
resources are released — which is why the pattern in that file re-raises
`CancelledError` rather than swallowing it. Swallowing it produces a task
that cannot be stopped, which is its own availability problem.

## Data

There is none. No personal data, no credentials, no fixtures containing
anything about a real person. The fixture server's responses are of the form
`waited 0.100s for /item/7`. The only inputs are integers and paths this lab
generated itself.

## What this lab does not cover

- **Securing a multi-process application.** Process pools here run trusted
  local code. Anything that unpickles data from an untrusted source is a
  different subject with a much sharper edge — `pickle` executes code during
  deserialisation by design.
- **Distributed task queues.** Celery and its relatives are named in the
  lesson's Alternatives section and are not run here. Their security model —
  the broker, its credentials, and what a worker will accept as a task — is
  substantial and is not taught by this lab.
- **Thread-safety of third-party libraries.** No third-party package is used
  here, and the suite enforces that. When you do use one, "is this object
  safe to share between threads?" is a question with a documented answer far
  more often than people check.
