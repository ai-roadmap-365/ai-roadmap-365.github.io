# Security notes — Day 072 lab

- **What the lab does.** It runs two small pytest suites over a CSV-backed
  practice log. Every file it writes goes into a temporary directory that
  pytest creates for the test that asked for it, and the bash harness makes
  its own scratch directories with `mktemp -d` and removes each one as that
  check finishes. Nothing here opens a network socket, reads the clock, needs
  a privilege, or touches a path you did not point it at.

- **The one networked moment is the install.** `pip install -r
  requirements/requirements.txt` downloads pytest from the Python Package
  Index. That is the only step in this lab that leaves your machine, and it
  is worth treating as a real trust decision rather than a formality:

  - Install into a **virtual environment** (`python3 -m venv .venv`), never
    into the system Python. A lab-local `.venv` can be deleted; a damaged
    system Python cannot be deleted so casually.
  - **Pin the version.** `pytest==9.1.1`, not `pytest`. An unpinned
    requirement means the bytes you install today and the bytes a colleague
    installs next month are not the same bytes, and neither of you can say
    what changed.
  - **Check the name.** Typo-squatting on package indexes is a real and
    recurring attack: a package one character away from a popular name,
    published to catch mistyped installs. Read the requirement line before you
    run the command.
  - Everything installed here is free and open source under the MIT licence,
    and pytest's own documentation is the place to confirm that rather than
    taking this file's word for it.

- **`tmp_path` is a security feature, not just a convenience.** A test that
  writes to a hard-coded path — `/tmp/test.csv`, or worse, a file beside the
  source — can clobber real data, can collide with another test, and can leave
  residue that makes the next run pass for the wrong reason. `tmp_path` gives
  every test a fresh directory nobody else is using, and pytest keeps only the
  last few runs so the disk does not fill. Every fixture in this lab that
  needs a file builds it from `tmp_path`.

- **`monkeypatch` undoes itself, and that matters.** The lab's built-in
  fixture demonstration sets an environment variable with
  `monkeypatch.setenv` and a later test asserts the variable is gone.
  Hand-rolled patching — assigning to `os.environ` directly, or replacing a
  module attribute — survives the test that did it, so a test that changed a
  credential path or an endpoint can silently change what a *later* test
  talks to. Undo-on-teardown is not tidiness; it is containment.

- **Test data is data.** The practice log in this lab is invented and
  harmless. Real suites are where production exports quietly end up as
  "fixtures", and a fixture file is a file in version control forever, visible
  to everyone with repository access and to every future clone. Generate test
  data, or anonymise it deliberately; never paste a production extract into a
  test directory.

- **Never put a credential in a test, a fixture, or a `conftest.py`.**
  `conftest.py` looks like configuration and gets read less carefully than
  application code, which makes it a favourite hiding place for an API key
  someone added "just to get the suite running". Read secrets from the
  environment, and let `monkeypatch.setenv` supply a fake one inside the test.
  Day 74 goes further into testing at boundaries, which is where this problem
  properly belongs.

- **A test suite is executable code with your permissions.** `conftest.py`
  files are imported and run automatically, from every directory pytest walks
  through, before any test does. That is exactly why you should read the test
  directory of an unfamiliar repository before running its suite — the same
  care you would give any script you downloaded. The suites in this lab do
  nothing but define fixtures and assertions; you can confirm that by reading
  them, which takes about two minutes.

- **What the harness deliberately breaks, and where.** One check copies
  `examples/` into a `mktemp -d` directory, damages a single comparison with
  `sed`, and confirms the suite fails. The damage happens only to the copy,
  the copy is removed immediately afterwards, and the lab's own files are
  never modified. If you reproduce that check by hand, do the same — copy
  first, and delete the copy when you are done.
