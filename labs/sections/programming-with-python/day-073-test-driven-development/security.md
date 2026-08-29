# Security notes — Day 073 lab

- **What the lab does.** Runs pytest over two small Python files that import
  nothing, and reads seventeen text files. It makes **no network connections**
  at test time, needs **no privileges**, and writes nothing into the lab
  directory. The mutation checks copy the implementation into a directory
  created with `mktemp -d` and delete it as each check finishes.

- **The single network moment.** `pip install -r requirements/requirements.txt`
  downloads pytest from the Python Package Index. That is the one command in
  this lab that reaches the internet, and it is worth treating as such: the
  version is pinned exactly (`pytest==9.1.1`) so you get the artefact the
  captures were made against rather than whatever is newest, and the install
  goes into a lab-local `.venv/` rather than your system Python, so a bad
  package cannot affect anything outside this directory. Deleting `.venv/`
  undoes it completely.

- **A test suite is executable code you are inviting in.** pytest imports and
  runs every `test_*.py` file it collects, with your user's permissions.
  Running someone else's suite is running someone else's program — read a test
  file from an unfamiliar source before you run it, exactly as you would a
  script. Everything in this lab is readable in under five minutes, and none
  of it opens a file, spawns a process, or touches a socket.

- **Writing the test first is a security practice, not only a design one.**
  The refusals in cycles 5, 6 and 7 exist because a scorer that silently totals
  `[11, -1, 99]` produces a number that looks like an answer. Stating each
  refusal as a failing test *before* the code exists is what forces the input
  rules to be decided deliberately, at the boundary, instead of being inferred
  later from whatever the implementation happened to tolerate. Most input
  validation that is missing in production is missing because nobody ever wrote
  the sentence "this input must be refused" anywhere.

- **`assert` in a test is not `assert` in production.** Python's `-O` flag
  removes `assert` statements entirely. That is harmless here, because pytest
  never runs with `-O`, but it is the reason you must never use a bare `assert`
  as a security check in shipped code. Refusals belong in an explicit `raise`,
  which is exactly what `ScoringError` is.

- **Never let a red test through by weakening it.** The most common way a real
  vulnerability gets shipped is not a missing test — it is a test that failed,
  and was adjusted until it passed. If cycle 6's refusal test fails, change the
  implementation. Changing the test to expect twelve pins in a frame makes the
  suite green and the program wrong, and the green suite then lends its
  authority to the bug.

- **The recorded history is evidence, and evidence can be forged.** The runner
  verifies that each cycle's captures chain consistently (cycle 5's red must
  show four earlier tests already green), which makes a fabricated record
  expensive rather than impossible. Treat that as the honest limit of any
  process artefact: it raises the cost of lying, it does not make lying
  impossible. The only real guarantee comes from tests you can re-run yourself,
  which is why `tests/run_tests.sh` re-runs everything from source rather than
  trusting a stored result.

- **No personal data anywhere.** The lab handles lists of integers between 0
  and 10. Nothing here should ever be pointed at real user data; if you extend
  the kata with data of your own, keep it out of version control.
