# Security notes — Day 076

## What this lab does to your machine

It reads and writes Python files inside its own directory, creates
temporary directories under your system temp path and deletes them again,
and runs two programs you installed yourself. It opens no network
connection, needs no API key, asks for no credentials, and never runs with
elevated privileges. `sudo` appears nowhere in this lab and should not be
used with it.

## A linter is a security control, and this is not a metaphor

Two of the rule families the reference configuration selects exist to catch
things that get people breached.

`S`, the **bandit**-derived family, flags patterns with a security history:
`subprocess` calls with `shell=True`, `yaml.load` without a safe loader,
`pickle` on untrusted input, hard-coded passwords, `assert` used for a
runtime check in production code (because `python -O` strips asserts), and
temporary files created with predictable names. None of these is
necessarily wrong. All of them are worth a second look, which is exactly
what a linter finding is.

`B`, the **bugbear** family, catches correctness traps that become security
bugs under the right conditions. `B006` — the rule this lab is built around
— is the clearest case. A mutable default argument is shared state that
outlives the call. In `add_item` it means two shoppers share a trolley. In a
web request handler with `def handler(request, cache={})`, the same defect
means data from one user's request is visible in the next user's response.
That is a cross-request data leak, and it looks exactly as innocent as the
line in this lab's messy module.

Run the demonstration yourself, from `examples/messy/`:

```bash
python3 -c "
import receipts
print(receipts.add_item('apple', 120))
print(receipts.add_item('pear', 95))
"
```

The second call prints both items. Nothing carried them across except a
default argument evaluated once, when the `def` line ran.

## Why `S101` is ignored in tests, and only in tests

The reference `pyproject.toml` relaxes `S101` for `test_*.py`. The rule is
right in general — `assert` is compiled away under `python -O`, so an
`assert` guarding a real invariant in shipped code can vanish silently. In
a test file, `assert` *is* the mechanism, tests are never run under `-O`,
and the rule is pure noise.

Note the shape of that decision. The rule was not deleted from `select` and
it was not added to the global `ignore`. It was relaxed in the one file
pattern where it is wrong, with a comment saying why. Every rule you switch
off globally is a rule that stops protecting the code where it still
applied.

## Suppression comments are a security surface

`# noqa` is how you tell the linter to be quiet about one line. There is a
right way and a wrong way, and the difference matters.

```python
import config  # noqa: F401   — re-exported for backwards compatibility
```

That names one rule, on one line, with a reason. A reviewer can check it in
five seconds.

```python
import config  # noqa
```

That silences **every** rule on that line, forever, including rules that did
not exist when it was written and including security rules. A bare `# noqa`
sprinkled through a codebase is a set of blind spots nobody can audit. Ruff
can find them for you — the rule `PGH004` flags blanket `# noqa` directives,
and `RUF100` flags suppressions that no longer suppress anything, which is
how you stop them accumulating.

The same logic applies to `# type: ignore` from yesterday's lesson. Name
the code, give the reason, or fix the problem.

## Running someone else's configuration

`pyproject.toml` is data, not code — Ruff parses it, it does not execute
it. A malicious `pyproject.toml` cannot run commands on your machine
through Ruff. It *can*, however, quietly switch off the rules that would
have protected you, which is a good reason to read the `ignore` list of any
project you join and ask what each entry is hiding.

`pre-commit`, discussed in the lesson, is a different matter: it downloads
and runs hook repositories you name in `.pre-commit-config.yaml`. Pin those
to a specific revision, and read what you are pinning.

## Data

Nothing in this lab handles personal data. The receipts are three fictional
grocery items with prices in cents. Nothing is written outside the lab
directory and your system temp path, and nothing persists between runs
except the tool caches, which contain only hashes and analysis results for
files you already have.
