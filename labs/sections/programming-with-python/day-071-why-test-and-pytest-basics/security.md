# Security notes — Day 071 lab

## What this lab does to your machine

It creates a virtual environment in `.venv/`, installs one package into it,
reads text files, and runs Python in temporary directories made with
`mktemp -d` and removed when each check finishes. It writes nothing outside
this lab directory and the system temporary directory. It does not need `sudo`
at any point, and if a command ever asks you for a password, something is
wrong — stop and read it.

## The network moment

Exactly one command in this lab touches the network:

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That downloads pytest and its four small dependencies from the Python Package
Index. After it finishes, every other command in the lab runs fully offline —
the test suite included. `metadata.yml` therefore records
`requires_network: true`, which is honest about the install even though the
tests themselves never open a socket.

Two habits worth forming now, because installing packages is where most Python
supply-chain incidents begin:

- **Pin versions.** `pytest==9.1.1`, never `pytest`. An unpinned dependency
  means the code you audited on Monday is not the code that runs on Friday.
- **Read the name you are typing.** Typo-squatting — a package whose name is
  one character away from a popular one — is a live and ordinary attack. The
  package you want here is `pytest`, spelled exactly that way.

## Installing into a virtual environment, not the system Python

`python3 -m venv .venv` gives this lab its own copy of pip and its own
`site-packages`. Two reasons that matters beyond tidiness:

- a package installed here cannot overwrite or shadow anything your operating
  system depends on;
- deleting the directory removes every trace of it, with no uninstall step and
  nothing left in a system path.

Never install a lab's requirements with `sudo pip install`. Any code in any
package can run at install time.

## Test code is code

This is the security lesson of the day, and it is routinely forgotten.

pytest **imports** every file it collects. Importing runs the module body. So
a file called `test_anything.py` dropped into a directory you run pytest over
executes with your privileges, before a single assertion is evaluated. The
same is true of `conftest.py`, which pytest imports automatically without any
file naming it. Consequences:

- treat test files from an untrusted source exactly like any other code you
  are about to run — read them first;
- be careful what you point pytest at. `pytest /some/downloaded/directory`
  imports everything test-shaped underneath it;
- a `conftest.py` is the quietest place in a Python repository to hide code
  that runs on every test invocation. When you review a pull request, read the
  `conftest.py` diff as carefully as the source diff.

Nothing in this lab does anything of the sort — every file here is short
enough to read in a minute, and you should.

## Assertions and `python -O`

Python's `-O` flag strips `assert` statements from compiled code entirely.
That is why `assert` is a fine tool for *tests*, which are never run optimised,
and a poor tool for *runtime* validation of untrusted input, which may be. A
security check written as `assert user.is_admin` disappears under `-O` and the
program carries on as if it had passed. Validate with an explicit `if` and a
raised exception, exactly as Day 70's domain model does; keep `assert` for
tests.

## Secrets

This lab has no credentials, no API keys, and no configuration file that would
hold any. When you later write tests for code that does, three rules:

- never put a real credential in a test file — test files are committed, and
  committed secrets are permanently leaked even after the commit is amended;
- never test against production data or a production service;
- redact before you print. A failing assertion prints both sides of the
  comparison, so a test that asserts on an object containing a token will put
  that token in a build log, and build logs are widely readable.

Day 074 makes this concrete: you will stub the outside boundary rather than
call it, which removes the credential from the test entirely.

## What the test runner does with temporary files

`tests/run_tests.sh` copies small files into directories created with
`mktemp -d`, breaks one line with `sed`, runs pytest there, and deletes the
directory. It never edits a file inside the lab, so a failing run cannot
corrupt your work. Every destructive command it issues names an exact path it
just created — there is no wildcard deletion anywhere in it.

## Privacy

No telemetry. pytest does not phone home, does not require an account, and
collects nothing. The only data leaving your machine in this lab is the HTTPS
request pip makes for the package itself.
