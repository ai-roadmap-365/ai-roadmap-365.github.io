# Security notes — Day 100 lab

This lab is arithmetic on twelve small integers. It is one of the least
dangerous things in the course. The notes below are short because there is
little to say, and they are here rather than absent because "there is nothing
to worry about" is a claim that should still be checked.

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
  finishes there is nothing left inside it either. Sections 7 of the harness
  checks for stray `__pycache__` and `.pytest_cache` directories and fails if
  it finds one.

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

Everything in `examples/dataset.py` is invented — the garden centre, the three
potting mixes, the four ingredients and the prices. It resembles no real
business and contains nothing personal. If you replace it with data of your
own, be aware that a matrix is exactly the shape real personal data arrives
in: rows are people and columns are facts about them. The moment you paste
that into a lab directory, ordinary care applies again — do not commit it, do
not copy it somewhere it does not belong, and prefer a small invented sample
for anything you are only using to learn.

## The view-versus-copy exercise, read as a safety property

Exercise 3 is a memory-sharing demonstration, and it has a security-flavoured
lesson underneath the pedagogy: **a function that receives a NumPy array can
modify the caller's data without returning anything.** A slice, a reshape or a
transpose handed across a function boundary carries write access with it. That
is not a vulnerability in NumPy — it is documented, and it is the reason NumPy
is fast — but it does mean that "I only passed it a view" is not the same as
"I only let it read". If you need a guarantee, pass `arr.copy()`, or set
`arr.flags.writeable = False` on the view before handing it over.
