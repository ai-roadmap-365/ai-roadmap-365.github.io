# Security notes — Day 070 lab

- **What the lab does:** reads only the files that ship with it, and writes a
  single `club.json` into whatever directory you run a demo from. It makes
  **no network connections**, needs **no privileges**, and touches nothing
  outside the directory you are standing in. The test runner does its file
  work inside directories created with `mktemp -d` and removes each one as
  that check finishes.

- **Validation at construction is a security control.** This is the security
  lesson of the day, and it is a design property rather than a checklist item.
  When the only way to obtain a `MembershipNumber` is through code that
  matches it against a pattern, and the only way to obtain a `Money` is
  through code that rejects negatives, non-integers and malformed currency
  codes, then *no* code path anywhere in the program can produce an invalid
  one. Compare that with validating in the import script: every future caller
  — a correction path, an admin command, a migration — is a fresh chance to
  forget, and the one that forgets is the one an attacker finds.

- **Trust boundaries are where objects are built, not where files are read.**
  The repository's `load` deliberately rebuilds every value through the domain
  constructors instead of setting fields directly. That is why a hand-edited
  `club.json` with `"price_cents": -1` is refused with `InvalidMoney` rather
  than silently loaded. Treat any file you did not write in this run as
  untrusted input, even one your own program wrote a minute ago — a file is a
  place other processes and other people can reach.

- **A core that cannot do I/O cannot be made to.** `gym_core.py` imports
  `dataclasses`, `datetime`, `enum` and `re`, and nothing else. It has no
  `open`, no `subprocess`, no `os`, no socket. Whatever malformed input it is
  handed, the worst it can do is raise. Every dangerous capability in the lab
  is confined to two small, readable files at the edge — which are the files
  you audit. This is the practical payoff of the boundary, beyond
  testability.

- **Deserialised data is data, never code.** `json.loads` is safe by design:
  it can only ever produce dicts, lists, strings, numbers, booleans and
  `None`, or raise. Python's `pickle` is the opposite — unpickling runs code —
  and must never be pointed at a file you did not create yourself in the same
  process. If you extend this lab with another storage format, keep that line:
  never `eval()` a value out of a file, and never use `ast.literal_eval` as a
  substitute for a real parser on untrusted input.

- **A closed set is a safety mechanism.** `PlanTier` being an enum means an
  unknown tier from a tampered file is refused at load time with a
  `ValueError`, instead of becoming a member with an undefined check-in limit.
  Every closed set you leave as a bare string — a role, a permission level, an
  account status — is a place where a value nobody anticipated can flow
  straight through your checks. This is why "stringly typed" appears on the
  anti-pattern list next to genuine bugs.

- **Errors should say what happened, to you, and less to everyone else.** The
  domain errors here name the rule and the offending value, which is right for
  a local tool. In a networked program the same message may not be safe to
  return to a caller: it can disclose membership numbers, whether a given
  record exists, or the shape of your storage. The pattern that scales is the
  one this lab sets up — the adapter, not the model, decides what the outside
  world is told, so you can log the detailed message and return a generic one.

- **Membership records are personal data.** Names, join dates and attendance
  patterns are exactly the sort of content that turns a convenient JSON file
  into a privacy incident when it is copied to a laptop, pasted into a chat,
  or committed to version control. The `club.json` this lab writes contains
  invented people; keep real ones out of repositories, and delete extracts
  when the job they were made for is finished.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/gym_core.py`, `examples/gym_repository.py`,
  `examples/demo.py` and `tests/run_tests.sh` before running them. Running
  unread scripts is one of the most common ways developers get compromised;
  the course's rule is that every lab script is small enough to read and
  understand first.
