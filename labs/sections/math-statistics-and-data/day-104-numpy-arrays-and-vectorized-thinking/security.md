# Security notes

## What this lab does

It computes and it prints. That is all.

- **No files written.** Nothing in `examples/` or `starter/` opens a file for
  writing. The only files that appear are Python's bytecode caches, and the
  harness exports `PYTHONDONTWRITEBYTECODE=1` and passes `-p no:cacheprovider`
  to stop even those.
- **No network.** After the one-time `pip install`, nothing here opens a socket.
  Section 7 of `tests/run_tests.sh` greps every source file in `examples/` and
  `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://` and
  fails if it finds any.
- **No credentials, no keys, no accounts.** `requires_api_key` is false in
  `metadata.yml` and there is nothing to put in it.
- **No `sudo`, ever.** The virtual environment lives inside the lab directory
  and `rm -rf .venv` is a complete undo.
- **All data is invented.** The twenty readings come from a seeded generator.
  The six articles do not exist and their feature counts were chosen by hand so
  the arithmetic can be checked with a pen.

## Installing two packages is a supply-chain decision

`pip install` downloads and executes code from a package index. It is the one
genuinely privileged act in this lab, and it deserves naming rather than
skipping past.

Two mitigations are in place here and both are worth carrying into your own
work. The versions are **pinned exactly** in `requirements/requirements.txt`, so
a later release cannot arrive silently in the middle of a course. And the
install goes into a **lab-local virtual environment**, so nothing it brings can
affect the rest of your machine, and deleting one directory removes all of it.

Neither of those is a substitute for knowing what you are installing. NumPy is
about as well-scrutinised as open-source software gets — but "everyone uses it"
is a reason to check the name you typed, not a reason to skip checking. A
mistyped package name is the oldest attack in the ecosystem.

## The one security-relevant idea in the day itself

**Silent integer overflow.**

`np.array([127], dtype=np.int8) + 1` is `-128`. No exception. No warning, on
numpy 2.5.2, measured rather than assumed. The program carries on with a
negative number where it expected a large positive one.

Put that in a length check, a quota, a byte count, an index, a remaining-balance
calculation, and you have a class of bug that has been exploited for decades: a
value that was supposed to be too big becomes negative, the "is it too big?"
test passes, and the code proceeds on an assumption that is now false.

Python itself does not have this problem, because a Python `int` grows to
whatever size it needs. The moment you put data into a fixed-width array, you
have opted into a promise about range — and NumPy will keep that promise even
when keeping it produces nonsense. The dtype is the promise. Choose it on
purpose, and check `a.dtype` first whenever a number looks impossible.

The float version is quieter and no less real. Above 2^24 a float32 cannot tell
16,777,216 from 16,777,217 at all, so an accumulator in float32 can stop
increasing while you are still adding to it.

## The second one: views share memory

A slice, a transpose and a reshape hand back a *view* — a different way of
reading the same bytes. Writing through one writes through to the other.

If you hand a caller `data[0:100]` believing you have given them a copy of the
first hundred rows, you have given them a window onto your array, and anything
they write lands in yours. The habit worth forming is that returning a view is a
decision: `np.shares_memory(a, b)` answers the question, and `.copy()` settles
it.

## What this lab is not

It is not a benchmark you should cite. The timings are one machine on one day
and are labelled that way everywhere they appear. Nothing here asserts a
duration; the tests assert only that the vectorised version is at least twenty
times faster, which is a claim about the shape of the gap.
