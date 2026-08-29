# Security notes — Day 109

This lab computes and prints. It writes no files, opens no network connection
after the one-time package install, needs no credentials, no API key and no
`sudo`, and every number in it is invented or derived from something invented.

Still, three things here generalise to code you will write for real, and one of
them is a security concern rather than a correctness one.

## What this lab actually does to your machine

| Concern | This lab |
| --- | --- |
| Network | One `pip install` of numpy and pytest. Nothing else. Section 7 of `tests/run_tests.sh` greps every source file in `examples/` and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://` and fails if any appears. |
| Filesystem | Reads its own source. Writes nothing outside the lab directory. `PYTHONDONTWRITEBYTECODE=1` is exported by the harness so not even a `__pycache__` is left, and a check confirms it. |
| Credentials | None used, none needed, none stored. |
| Elevated privileges | None. Never run any of this with `sudo`. |
| Ports | None bound. |
| Data | Six invented surfaces, five invented probe points, four invented samples for the model. Nothing was measured from anything real. |
| Isolation | Everything installs into a lab-local `.venv`. `rm -rf .venv` from the lab directory is a complete undo. |

## The one that is genuinely a security concern

**A numerical gradient calls the function you hand it, twice per input.**

`gradient(f, point)` on a function of `n` inputs evaluates `f` exactly `2n`
times. That is arithmetic, and the lab counts it. But it means that if `f` does
anything other than compute a number, that thing happens `2n` times.

If `f` writes a file, you get `2n` writes. If `f` charges an account, you get
`2n` charges. If `f` is a wrapper around a remote call, you have made `2n`
requests to compute one gradient — and Day 111 will call `gradient` in a loop.

This is the general shape of the problem: **a function passed as a value is
executed on someone else's schedule, not yours.** The lab's `Counter` class in
script 07 is a two-line demonstration of how to find out how often that
schedule fires before you commit to it. Wrapping an unfamiliar callable in a
counter and looking at the number is a habit worth having.

The related rule: never hand a numerical differentiator a function that has
side effects, and if you must, make the side effects idempotent first.

## The one that is a correctness concern that behaves like a security one

**A tolerance carried from one context to another can turn a check into
decoration.**

Every float comparison in this lab has a stated tolerance, and
`starter/surfaces.py` explains where each one came from. `GRADIENT_TOL` is
`1e-8`, and script 05 shows exactly where that stops being achievable: at the
point `(1000, -1000)` a plane's gradient is still exactly `(3, -2)`, and the
numerical estimate of it is out by `5e-8` — five times the tolerance — purely
because the function's value is large and roundoff scales with it.

The failure mode to recognise is the fix that gets applied at that moment.
Someone widens the tolerance to `1e-6` to make the test pass, and now a test
that was checking a gradient is checking nothing at all, while continuing to
report a green tick. A check that cannot fail is worse than no check, because
it is a check other people will rely on.

The honest fixes are to scale the inputs, to use a relative tolerance rather
than an absolute one, or to say plainly that this method does not work here.
The lab does the third: `test_the_numerical_gradient_stops_meeting_the_labs_tolerance_far_from_home`
asserts the failure rather than papering over it, so the boundary is documented
by the suite instead of being discovered by whoever comes next.

## The third, which is about trusting a library's defaults

`numpy.gradient` defaults to `edge_order=1`, which uses a first-order one-sided
formula at the boundary of the array. On an exactly sampled quadratic, every
interior value is exact and the corner is wrong — `(0.5, 1.5)` where `(0, 0)`
is correct. Nothing warns you. Passing `edge_order=2` fixes it exactly.

There is no vulnerability here, and NumPy is behaving as documented. The point
is that "it ran without error and the numbers looked plausible" is not
evidence, and it is the same reasoning that lets a misconfigured check pass in
a security context. The lab asserts both behaviours — the exact interior and
the first-order corner — so that a future release changing either one would be
reported rather than silently absorbed.

## If you extend this lab

- Keep everything inside the lab directory.
- Do not add anything that reads a URL, a credential file, or an environment
  variable you did not set yourself.
- If you add a tolerance, write down where it came from in the same commit. A
  tolerance with no derivation behind it is a number someone will later widen.
- If you differentiate a function that touches anything outside itself, count
  the calls first.
