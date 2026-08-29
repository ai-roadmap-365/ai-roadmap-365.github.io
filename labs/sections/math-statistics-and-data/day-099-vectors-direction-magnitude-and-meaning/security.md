# Security notes

This lab does arithmetic on lists of small numbers. Its attack surface is close
to zero, and most of what follows is about the habits worth keeping rather than
about risks in this particular directory.

## What this lab does

- Reads and writes nothing on disk. Every vector is a literal in a source file.
- Opens no network connection at run time. The harness greps the lab's own
  `.py` files for `requests.`, `urlopen`, `httpx.` and `socket.` and fails if
  any appears.
- Runs no subprocess except the ones `tests/run_tests.sh` starts: `python3` and
  `pytest`, both resolved from `PYTEST`/`PYTHON`, then `./.venv/bin/`, then
  `PATH`.
- Needs no elevated privileges. If anything here asks for `sudo`, something is
  wrong.
- Writes only inside two temporary directories created with `mktemp -d`, both
  removed before the harness exits. They exist so the suite can prove itself
  non-vacuous by breaking a copy of the implementation — never the original.

## The one network step

`pip install -r requirements/requirements.txt` downloads NumPy and pytest from
the Python Package Index. That is the only moment this lab touches a network,
and `requires_network: true` in `metadata.yml` records it.

Two habits worth keeping, both visible in this lab:

**Pin versions.** `requirements.txt` names exact versions rather than ranges.
That is reproducibility first, but it is also supply-chain hygiene: an
unpinned dependency means a future release — including a compromised one — gets
installed silently on the next machine that runs your code.

**Install into a virtual environment, not system-wide.** A `.venv` inside the
lab confines the install to this directory. A `sudo pip install` puts arbitrary
downloaded code into the interpreter every program on the machine uses.

If you want the install to be verifiable rather than merely pinned, `pip` can
be given hashes:

```bash
pip install --require-hashes -r requirements.txt
```

That form requires every line to carry a `--hash=sha256:...`, and refuses to
install anything whose download does not match. This lab does not use it —
generating and maintaining hashes is out of scope for a day about vectors — and
saying so plainly is the honest position.

## Where vector code does become a security question

None of this bites in a lab with six hand-made vectors, but all of it bites in
the systems the lab is preparing you for, and it is better to meet the ideas
now than to meet them in production.

**Embeddings are not anonymised data.** It is easy to assume that turning a
document into 768 floating-point numbers has destroyed the original. It has
not. Embedding-inversion research has repeatedly recovered substantial parts of
the source text from its vector. Treat an embedding of personal data as
personal data: same access controls, same retention rules, same deletion
obligations.

**A vector database is a database.** The same questions apply as to any other
store: who can read it, who can write to it, is it encrypted at rest, what
happens when somebody exercises a deletion right. "It is only numbers" is not
an answer to any of those.

**Nearest-neighbour results leak.** If a search returns the closest documents
to a query, and some documents are ones the querying user is not allowed to
see, then the ranking itself is a disclosure — you learn something exists, and
roughly what it resembles, without ever being shown it. Access control belongs
in the retrieval step, not in the rendering step.

**Unbounded input dimensions.** Code that accepts a vector from a caller and
loops over its components should check the length before it allocates. A
request claiming a million dimensions is a cheap denial of service if nothing
refuses it. The `check_same_dimension` guard in this lab is written for
correctness rather than for defence, but it is the same instinct: validate
shape at the boundary.

**Floating point is not a security control.** A comparison written with `==`
on floats can be made to behave differently by tiny changes in input, which is
a correctness bug in a lab and can be an exploitable one in a threshold check —
"is this similarity above 0.95?" is a decision, and decisions made on
unstably-compared floats are decisions an attacker can nudge. Use an explicit
tolerance, and choose it deliberately.

## Data in this lab

The six article names and their four hand-counted features are invented for
this exercise. They describe nothing and nobody real, and no personal data of
any kind appears in this directory.
