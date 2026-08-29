# Security notes — Day 103 lab

This lab is arithmetic on twenty-four small integers and some seeded random
numbers. It is one of the least dangerous things in the course. The notes below
are short because there is little to say, and they are here rather than absent
because "there is nothing to worry about" is a claim that should still be
checked.

## What this lab does to your machine

- **It computes and prints.** No file is created, no database is opened, no
  process is started, no port is bound.
- **It opens no network connection.** Not once, in any script or test. Section
  7 of `tests/run_tests.sh` greps every file under `examples/` and `starter/`
  for `urlopen`, `requests.`, `socket.`, and `http`, and fails if any of them
  appears.
- **It needs no credentials.** No account, no key, no token, no paid service.
- **It needs no `sudo`.** If any instruction in this lab appears to require
  elevated privileges, that instruction is wrong; stop and re-read it.
- **It writes nothing outside its own directory**, and by the time the harness
  finishes there is nothing left inside it either. Section 7 checks for stray
  `__pycache__` and `.pytest_cache` directories and fails if it finds one.

## The one thing that touches the network

`pip install -r requirements/requirements.txt` downloads two packages from the
Python Package Index. That is the whole network story, it happens once, and
after it you can disconnect for good.

Two habits from Day 43 still apply and are worth restating:

- **Install into a virtual environment, not the system Python.** The commands
  in this lab create `.venv/` inside the lab directory precisely so that a
  mistake here cannot affect anything else on your machine, and so that
  `rm -rf .venv` is a complete undo.
- **Read the package name before you press return.** Typo-squatting on package
  indexes is real: a package named one character away from `numpy` is not
  NumPy. The pinned file spells both names out so you are copying rather than
  typing.

## About the data

Everything in `examples/catalogue.py` is invented — the six articles, the four
features and every count in the table. They resemble no real publication and
contain nothing personal. They are the same numbers Day 99 used, deliberately,
so that you can see one dataset answer two different questions.

If you replace them with data of your own, notice what an embedding table
actually is: one row per document, and enough numbers in that row to
distinguish that document from every other. That is a fingerprint. Two
consequences worth carrying:

- **Embeddings are not anonymous.** A vector derived from a person's text is
  derived from a person's text, and similarity search over it can link
  documents back to their author whether or not a name was ever stored. Treat
  an embedding store with the same care as the documents it came from.
- **Similarity search leaks by design.** The whole purpose of the index is to
  answer "what else is like this", and that is precisely the query an attacker
  with access to the index would want to run. If some documents in a store are
  more sensitive than others, the access control has to live at the retrieval
  step, not only at the document store — otherwise a search that returns a
  snippet has published the snippet.

Neither point is speculative and neither is exercised by this lab, which uses
six invented articles about roast chicken and the weather. They are here
because this is the day you learned how retrieval works, and it is the right
day to learn what it exposes.

## About the random numbers

`examples/07_curse_of_dimensionality.py` uses `numpy.random.default_rng(103)`.
That is a **seeded, reproducible** generator chosen so the measurement can be
checked. It is not a cryptographic random source and must never be used as
one. When you need unpredictability rather than reproducibility — tokens,
passwords, keys, nonces — use Python's `secrets` module, which draws from the
operating system's cryptographic source. The distinction is not academic: a
seeded generator is *designed* to produce the same stream every time, which is
exactly the property you want in a test and exactly the property that makes a
secret worthless.

## One correctness habit that is really a safety habit

`cosine_similarity` in this lab raises `ValueError` on a zero vector rather
than returning `NaN`. That looks like fussiness and it is not. An empty
document, a failed extraction or a truncated file all produce a zero vector in
a real pipeline. A `NaN` from one of them sorts unpredictably, spreads through
every average it touches, and produces a ranking that is quietly wrong with
nothing in the logs. Failing loudly at the point of the bad input is cheaper
than discovering the bad output three systems later.
