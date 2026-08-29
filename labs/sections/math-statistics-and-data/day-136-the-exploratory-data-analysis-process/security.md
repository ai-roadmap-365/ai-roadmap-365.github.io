# Security notes

This lab computes and prints. It does not write files outside itself, does
not open a network connection after the one-time dependency install, needs
no credentials, no API key, and no `sudo`. Every dataset used anywhere in
it is generated in-process from a seeded random number generator; nothing
is downloaded, and nothing here touches a real customer, user, or any
other real person's data.

## What each script actually does

- Reads: its own source, `dataset.py`, `exploration.py`, and (for the
  virtual environment) `requirements/requirements.txt`.
- Writes: nothing to disk by itself. `pytest`'s own bytecode caches
  (`__pycache__`, `.pytest_cache`) are the only files any command in this
  lab creates, and the test harness proves at the end of every run that
  none are left behind.
- Network: only `pip install -r requirements/requirements.txt`, once, to
  populate `.venv`. `tests/run_tests.sh` greps every file in `examples/`
  and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
  `https://` and fails the run if any is found.
- Randomness: every simulation is seeded (`numpy.random.default_rng` with
  an explicit integer), so every number in this lab is reproducible on
  the same package versions, and no result depends on system entropy.

## Three findings worth carrying into real work

1. **A p-value answers a narrower question than most people act on it as
   answering.** It is `P(data this extreme | null true)`, not
   `P(null true | data)` -- exercise 1 makes the gap between those two
   concrete: data with genuinely no signal in it produces a "significant"
   result most of the time once you look at enough of it.
2. **"We stopped when we found something" is not a stopping rule -- it is
   the mechanism that inflates false positives**, exercise 8's
   centrepiece. Deciding in advance how many questions you will ask, and
   asking them regardless of what turns up, is what a stopping rule has
   to do to be worth calling one.
3. **A correction needs an honest count to correct, and real exploration
   rarely produces one without deliberate effort.** Bonferroni is exact
   arithmetic; exercise 5 shows it working exactly as advertised when the
   comparison count is right, and failing by a wide margin when it is
   not. The research log (exercise 6) is not a compliance exercise -- it
   is the only thing standing between "I only ran one test" and a number
   anyone can check.

## If you adapt this lab to real data

The holdout mechanics (exercise 3) generalize directly: split before
looking, keep the confirmation half untouched until a hypothesis is
chosen, and treat the confirmation-set p-value, not the exploration-set
one, as the number that matters. If the real data includes anything
personally identifying, that is a separate concern this lab does not
address -- de-identification, access control, and retention policy are
outside its scope, and none of that machinery lives here.
