# Security notes

This lab reads no files, writes no files, opens no sockets, and needs no
credentials or privileges. Its security lessons are therefore not about this
code — they are about the habits it teaches, because inheritance and dunder
methods both quietly widen what your program will execute and what it will
disclose.

## Dunder methods run implicitly, where you will never see them in the source

This is the single most important idea on this page. When you write
`__repr__`, `__eq__`, `__hash__` or `__getitem__`, you are installing code
that the interpreter calls on your behalf, in places that do not mention your
class at all:

| Dunder | Runs implicitly when |
| --- | --- |
| `__repr__` | An exception traceback is formatted, an object is logged, or it appears inside any container being printed |
| `__str__` | Anything is `print`ed or interpolated into an f-string |
| `__eq__` | Any `in`, `==`, `.index()`, `.remove()`, or dict/set lookup that collides |
| `__hash__` | Every single set or dict operation touching the object |
| `__getitem__` | Any subscript, including ones written by library code |

Three rules follow, and they are real controls rather than style advice:

1. **Keep dunders free of I/O.** No file access, no network calls, no
   database queries, no logging. A `__repr__` that hits the network turns
   every traceback into a request, and a `__hash__` that reads a file turns
   every dict insert into disk activity.
2. **Keep dunders free of side effects.** Code that runs at unpredictable
   times must not mutate state. A debugger printing your object, or a test
   framework rendering an assertion failure, must not change your program.
3. **Keep dunders cheap.** `__hash__` runs on every set and dict operation
   and `__eq__` on every collision. Hash a small tuple of identifying
   fields — never a large nested structure.

## `__repr__` is a disclosure surface

Because `__repr__` is what appears in logs, error messages, crash reports and
tracebacks, whatever it prints will end up in places you did not choose:
aggregated logging systems, error-tracking services, terminal scrollback,
support tickets, and screenshots.

```python
class Customer:
    def __repr__(self):
        return f"Customer({self.email!r}, card={self.card_number!r})"   # leak
```

Every unhandled exception anywhere near that object now writes an email
address and a card number into a log line. Print identifiers, not payloads:

```python
class Customer:
    def __repr__(self):
        return f"Customer(id={self.id!r})"                              # safe
```

The same applies to `__str__`. Treat both as public output, because they are.

## `__eq__`, `__hash__`, and the security of lookups

Two rules that matter beyond correctness:

- **Equal objects must hash equal.** If they do not, a `dict` or `set` will
  fail to find entries it genuinely contains — a lookup that silently misses
  is an access-control bug waiting to happen when the structure is a cache,
  an allowlist, or a session store.
- **Hashing mutable state is a trap.** If a field used by `__hash__` changes
  after the object is placed in a set, the object is lost: it lands in the
  wrong bucket and can be neither found nor removed. Hash only fields that do
  not change for the object's lifetime.

Note that Python randomises string hashes per process by default, which is a
deliberate defence against hash-collision denial-of-service attacks. Never
persist a `hash()` value to a file or database and expect it to match on the
next run — use `hashlib` for anything that must be stable or cryptographic.
`hash()` is for in-memory lookup, nothing more.

## Inheritance widens what you trust

Subclassing a third-party class inherits **every** method it has — including
methods you have never read, and methods a future version may add or change.
Your object's behaviour is then partly defined by code outside your control,
and a library upgrade can alter it without a single line of your source
changing. This is the fragile base class problem viewed as a supply-chain
concern.

Composition trusts a much smaller surface: only the methods you actually
call on the object you hold. When you are integrating a dependency you did
not write, holding it as an attribute is the more conservative choice, and it
also makes the dependency easy to replace or to fake in a test.

## Abstract base classes are a guard rail, not a security boundary

`abc.ABC` catches an *honest mistake* — a subclass that forgot to implement
something — at construction time, which is genuinely valuable. It is not an
enforcement mechanism against hostile code: nothing stops a caller from
registering a virtual subclass, overriding `__subclasshook__`, or simply
ignoring the hierarchy. Use ABCs to help correct code stay correct, and use
real validation for untrusted input.

The same caution applies to `isinstance`. Duck typing means an object can
satisfy a protocol without your knowledge, which is exactly the flexibility
you want from `collections.abc` — and exactly why an `isinstance` check is
not proof that an object came from where you think it did.

## Things this lab deliberately never does

- **No `eval()` or `exec()` on data.** If you extend this lab to load menus
  from a file, parse them with `json`, never by evaluating the text. Turning
  data into code is how data becomes an attacker.
- **No `pickle`.** Unpickling runs arbitrary code by design, via the
  `__reduce__` dunder. Never unpickle data you did not create yourself. It is
  worth knowing that `__reduce__` is a dunder too — the data model is
  powerful in both directions.
- **No `sudo`, ever.** Nothing in this lab needs elevated privileges. If a
  command in a Python tutorial asks for `sudo`, stop and find out why first.
- **No network.** `requires_network` is `false` in `metadata.yml`, and that
  is checked, not merely claimed.

## Cleanup and blast radius

The test suite creates exactly one temporary directory with `mktemp -d` and
removes it through a `trap ... EXIT`, so it cleans up even if a check fails
partway through. It writes nowhere else, and neither does any example script.
The only files you should ever find modified after this lab are the two you
were invited to edit, `starter/kitchen.py` and `starter/comparison.md`.
