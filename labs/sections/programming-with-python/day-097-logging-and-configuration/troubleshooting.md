# Troubleshooting — Day 097

Grouped by the symptom you actually see. If your problem is not here, run
`bash tests/run_tests.sh` first: it prints what it expected and what it got for
every value it compares, which usually names the problem for you.

Almost every logging problem in this file has the same root cause, so it is
worth stating once at the top. **A log record has to pass two level checks and
then travel up a tree, and every one of those steps can silently drop it.** No
step raises an error when it drops something, because a logging call that
raised would take your program down at the worst possible moment. Silence is
the design, not the bug.

## Nothing comes out at all

**A logger at DEBUG and a handler at WARNING.**
The commonest one. `logger.setLevel(logging.DEBUG)` only opens the first gate.
Each handler applies its own level afterwards, and a handler created without an
explicit level starts at `NOTSET`, which for a handler means "pass everything"
— but `basicConfig` and `dictConfig` will happily give it a level you did not
notice. Print both:

```python
print(logging.getLevelName(log.level),
      [logging.getLevelName(h.level) for h in log.handlers])
```

**No handler anywhere.**
If a record reaches the root logger and the root has no handlers, Python uses
its *last-resort* handler, which writes to `stderr` at WARNING and above with
no formatting. So `log.warning(...)` appears and `log.info(...)` vanishes,
which looks like a level bug and is actually a missing configuration. Call
`logging.basicConfig()` once, or configure properly with `dictConfig`.

**`propagate = False` somewhere above you.**
If a library — or an earlier line of your own setup — set `propagate = False`
on an ancestor logger, records stop there and never reach the handler you
configured on the root. Walk the chain:

```python
name, logger = "myapp.loader", logging.getLogger("myapp.loader")
while logger:
    print(logger.name or "root", logger.level, logger.handlers, logger.propagate)
    logger = logger.parent
```

**`disable_existing_loggers` silenced you.**
`dictConfig` defaults it to `True`, which disables every logger that existed
when the call was made — including the ones libraries create at import time.
Set it to `False` unless you specifically want that.

**A filter returned False.**
Filters run on the logger you called and on each handler. One returning a falsy
value drops the record with no trace. If you wrote a filter, make sure every
path through it returns `True`.

## Everything comes out twice

**A handler on your logger AND a handler on the root.**
A record travels up the dotted hierarchy and every handler it passes emits it.
The ancestors' *levels* are not consulted on the way up, only their handlers,
which is why this surprises people. `logging.basicConfig()` puts a handler on
the root, so calling it and then adding your own gives you two.

Two fixes, and they are not equivalent:

- `logging.getLogger("myapp").propagate = False` — right for a **library**
  whose records must not escape into an application it knows nothing about.
- Configure handlers in exactly **one** place — right for an **application**,
  because the alternative is a tree of loggers each with an opinion about where
  its output goes.

**You called `dictConfig` or added a handler twice.**
Module-level setup code that runs on every import, a `main()` called from a
test, a notebook cell run twice. `logging.getLogger("x").handlers` will show
you two identical handlers. `basicConfig` is idempotent-ish and does nothing if
the root already has a handler; `addHandler` is not.

## Messages, formatting, and arguments

**`ValueError: unsupported format character` or `not all arguments converted`.**
The message template is `%`-formatted, so a literal `%` in the text collides
with it once you also pass arguments. Write `%%`, or reword.

**Your f-string log line shows up but is expensive.**
That is the point of lazy formatting. `log.debug(f"{big!r}")` renders `big`
before `debug` is even called, whether or not anything will emit it.
`log.debug("%r", big)` renders it only if a handler will. The lab measures
this: 100 suppressed calls, 0 renders against 100.

**A `%s` line shows the template instead of the value.**
You passed the arguments as a tuple inside another tuple, or used `extra=` for
something that belongs in the message. `log.info("saw %s", n)` — the arguments
are positional, after the template.

**`KeyError: 'run_id'` from a formatter.**
Your format string references `%(run_id)s` but no record carries that
attribute. Either pass it through `extra=` on every call — miserable — or put
it in the formatter, as `JsonFormatter(static_fields=...)` does.

**`Attempt to overwrite 'message' in LogRecord`.**
`extra=` cannot contain a key that a `LogRecord` already uses: `message`,
`args`, `levelname`, `name`, `module`, `exc_info` and the rest. Rename your
field.

## Exceptions

**Your error line has no traceback.**
`log.error(str(error))` throws it away. Inside an `except` block use
`log.exception("what you were doing")`, which is `error()` with
`exc_info=True`. Outside an `except` block, `log.error("...", exc_info=error)`.

**`NoneType: None` appears under your message.**
`log.exception()` was called outside an `except` block, so there was no
exception being handled. Move the call inside, or pass `exc_info=` explicitly.

**Your logging call raised and took the program with it.**
It should not — the logging module catches handler errors and prints them to
stderr under `--- Logging error ---`. If you see that block, a formatter or a
filter of yours is raising. `logging.raiseExceptions = False` silences the
report; it does not fix the formatter.

## Redaction

**The filter appears to do nothing.**
Two causes, both measured in this lab.

*It is on a logger and the record came from a child.* A logger's filters run
only for records logged through that logger object; records propagating up from
a descendant skip them entirely. Attach the filter to each **handler**.

*The secret is inside an exception message.* The traceback is rendered by the
**formatter**, after every filter has run, so a filter that edits the record
never sees it. Either scrub in the formatter as well, or — better — never put
a credential in an exception message.

**The secret is redacted in some fields and not others.**
The filter has to walk nested structures. `{"headers": {"Authorization":
"Bearer sk-..."}}` needs recursion into the inner dict; a one-level pass
misses it.

## Configuration

**`TypeError: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`.**
`tomllib.load` takes a binary file object. `tomllib.loads` takes a `str`. This
catches everybody exactly once.

**`ModuleNotFoundError: No module named 'tomllib'`.**
Your Python is older than 3.11. Either upgrade, or `pip install tomli` and
import it under the same name — `tomli` is the same code and `tomllib` was
adopted from it.

**A flag you did not pass is overriding your environment variable.**
You gave argparse a `default=`, so "not passed" and "passed the default" became
the same value and the resolver cannot tell them apart. Set every flag's
argparse default to `None` and do the layering yourself. That is why
`build_parser` in this lab looks the way it does.

**`--no-something` does not exist, so the top layer cannot turn a flag off.**
A lone `--dry-run` with `action="store_true"` can only ever switch something
on. If the file or the environment said true, the highest-precedence layer has
no way to say false. Add the paired `--no-dry-run`.

**A boolean from the environment is always True.**
`bool("false")` is `True`, because every non-empty string is truthy. Use an
explicit word table and refuse anything not in it. The failure is silent, which
is what makes it worth a function of its own.

**`APP_X=` (empty) behaves like unset.**
You used `os.environ.get("APP_X")` and then `or default`, which collapses
never-set and set-to-empty into the same answer. Ask `"APP_X" in environ`
first, then decide what empty means for that setting.

**An integer setting fails with a confusing message.**
`int(" 128 ")` is fine; `int("12.5")` is not, and neither is `int("")`. Convert
inside a `try` and re-raise something that names the setting *and* where the
bad value came from — the second half is what turns a five-minute hunt into a
five-second one.

## The checkers and the tests

**`0 of 12 exercises complete.` with `NotImplementedError` on every line.**
That is the correct starting state. Work down `starter/01_logging.py` and
`starter/02_config.py`; each one starts reporting as you finish it.

**An exercise says "not yet" but your code looks right.**
Read the detail line under it — the checker prints what it wanted and what it
got. The commonest near-misses: exercise 2 with an f-string instead of lazy
formatting (`record.msg` no longer contains `%`), exercise 3 with the logger
lowered but not the handler, and exercise 12 with correct messages that do not
mention the provenance.

**`bash tests/run_tests.sh` fails on `left no __pycache__ behind`.**
Something ran without `PYTHONDONTWRITEBYTECODE=1` — usually a manual
`python3 examples/...` from an earlier session. Clean it:

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

**The suite fails on one of the two "surprise" checks.**
Those assert the two behaviours this lab measured rather than assumed: that a
filter on a logger does not protect records from child loggers, and that a
secret in an exception message survives a filter. If a future Python changes
either, these fail on purpose, so that the lesson gets corrected instead of
quietly becoming wrong. Read `expected-output/FIELDS.md`, confirm on your
interpreter, and report what you find.

## Windows

`tests/run_tests.sh` and `starter/03_check.sh` are bash scripts and use
`mktemp -d`, so run them under WSL and follow the Linux instructions. Neither
was run on native Windows when the expected output was captured, and no output
is claimed for it. The Python files themselves have nothing platform-specific
in them.
