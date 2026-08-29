# Security notes — Day 075 lab

## What this lab does to your machine

It installs two packages, reads local files, and runs local Python. mypy
analyses source without executing it; pytest executes the lab's own tests. No
script here opens a network connection, reads an environment secret, or writes
outside the lab directory. No API key is needed and none should be supplied.

The one networked moment is `pip install`, which fetches mypy and pytest from
the Python Package Index. Pinned versions in `requirements/requirements.txt`
are what make that reproducible: an unpinned install silently gives different
people different tools, and different tools give different answers.

## A type checker does not run your code — mostly

This is worth stating precisely, because it is a genuine safety property and
it has one genuine exception. mypy parses and analyses; it does not execute
your module bodies, so checking a file you have not read is far safer than
running it. The exception is `--install-types`, which downloads stub packages
from the index. That is an install, with all the trust that implies, and it is
why the flag is opt-in rather than automatic.

## The security claim types do NOT make

**An annotation is a claim about a value's type, never about its contents.**
Every one of these passes a type checker without comment:

```python
def open_report(path: str) -> str: ...      # path may be "../../etc/passwd"
def send_mail(to: str) -> None: ...         # to may be "not an email"
def run_query(sql: str) -> list[str]: ...   # sql may be an injection
```

`str` means "this is a sequence of characters". It does not mean safe,
validated, escaped, in range, or belonging to this user. A checker verifies
that values flow where their annotations permit; it has no opinion at all
about what the values are. Validation is a separate, runtime job — the
`__post_init__` checks from Day 69, an explicit guard, or a library like
pydantic that checks values at a boundary.

The most common expensive mistake here is treating a typed signature as an
input-validation layer at a trust boundary. It is not one, and it never was.

## Two settings that silently turn checking off

Both are legitimate tools and both deserve a comment explaining why they are
there.

**`Any`.** Not "some type" but "stop checking". A value typed `Any` can be
passed anywhere and have anything called on it, and the effect spreads
downstream to everything that touches it. `starter/any_demo.py` shows a real
`[union-attr]` error vanishing when one return annotation becomes `Any`, while
the code stays exactly as broken — the same call still raises `AttributeError`
at runtime. If an `Any` sits on a function that handles untrusted input, the
checking you thought you had over that whole path does not exist.

**`--ignore-missing-imports`** (and its per-module form). It tells mypy to
treat an unresolvable import as `Any`, which is sometimes the only practical
option — and which means every value from that dependency is now unchecked.
Scope it to the specific module in configuration rather than applying it
globally, and re-check periodically whether stubs have since appeared.

## `cast` is an assertion, not a conversion

`cast(str, value)` emits no runtime check and performs no conversion. It tells
the checker to believe you. If you are wrong, nothing objects at the cast and
the wrong type travels onward to fail somewhere with no obvious connection to
the mistake. Prefer `isinstance`, which narrows *and* checks. Where a cast is
genuinely necessary, write the reason beside it.

## `# type: ignore` hygiene

Always name the code: `# type: ignore[union-attr]`, never a bare
`# type: ignore`. A bare ignore suppresses every error on that line forever,
including ones introduced later by an edit nobody connected to it. Turn on
`warn_unused_ignores` so an ignore that has outlived its problem becomes an
error of its own — that setting is the difference between a small, current set
of documented exemptions and a large, stale one nobody dares touch.

## Privacy

mypy runs entirely on your machine. It reads your source, writes a cache into
`.mypy_cache/`, and prints to your terminal. That cache contains analysed
information derived from your source, so treat it exactly as you treat the
source: it is excluded from version control here, and you should not commit it
or attach it to a bug report without looking at it first.

If you use a hosted editor or an extension that runs a checker as a service,
that is a different arrangement with different data flow, and it is worth
reading what it sends before you enable it on a private codebase. Nothing in
this lab requires one.

## Continuous integration

mypy exits non-zero when it finds errors, which is what makes it usable as a
gate. Two cautions when you wire it into a pipeline. Pin the version, or a
release with new checks will fail a build nobody changed. And do not let the
gate be bypassed by adding ignores — a build that passes because the
exemption list grew is not a build that passed.
