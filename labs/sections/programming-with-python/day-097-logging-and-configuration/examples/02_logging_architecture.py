#!/usr/bin/env python3
"""The logging module's architecture, demonstrated one confusing behaviour at a time.

    python3 examples/02_logging_architecture.py

Six demonstrations, each one a thing that surprises people:

    A. the same script as 01_prints.py, converted
    B. the two-level trap — a logger at DEBUG whose handler is at WARNING,
       and the message that vanishes
    C. propagation, the duplicate message it causes, and two fixes
    D. exception() against error(str(e)), and what the second one throws away
    E. lazy formatting, and what it actually saves
    F. the five levels, chosen honestly

Every demonstration captures its own log output into a StringIO buffer rather
than letting it go to stdout, then prints the buffer. That is not a testing
trick bolted on afterwards — it is how you should capture logs in a test, and
it is why the output below is exactly the records that reached each handler
and nothing else.

One line of sanitising: demonstration D prints a real traceback, and a
traceback contains the absolute path of this file. The script rewrites that
path to `<lab>` before printing, so the captured output in expected-output/ is
identical on every machine. Nothing else is altered.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent


def banner(letter: str, title: str) -> None:
    print()
    print("=" * 70)
    print(f"{letter}. {title}")
    print("=" * 70)


def fresh_logger(name: str) -> logging.Logger:
    """A logger with no handlers and nothing inherited, for a clean demo.

    Reaching into `logger.handlers` like this is fine in a demonstration and
    is not how you configure a real application — `dictConfig` is, and
    demonstration 05 shows it. It is done here so each section starts from a
    known state regardless of what the section before it did.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True
    return logger


def attach_buffer(
    logger: logging.Logger, level: int, fmt: str = "%(levelname)-8s %(name)-16s %(message)s"
) -> io.StringIO:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    return stream


def show(stream: io.StringIO, label: str) -> None:
    text = stream.getvalue()
    print(f"--- {label} ---")
    if not text.strip():
        print("(nothing. Not one line.)")
    else:
        print(text.rstrip())


# ---------------------------------------------------------------------------
# A. The converted script
# ---------------------------------------------------------------------------

RECORDS = [
    {"id": 1, "text": "the cat sat on the mat", "label": "neutral"},
    {"id": 2, "text": "", "label": "neutral"},
    {"id": 3, "text": "shipping was late and the box was crushed", "label": "negative"},
    {"id": 4, "text": "arrived early, works perfectly", "label": "positive"},
    {"id": 5, "text": "no opinion", "label": "unknown"},
    {"id": 6, "text": "great value for the price", "label": "positive"},
]
VALID_LABELS = {"neutral", "negative", "positive"}


def prepare(records, log: logging.Logger):
    """01_prints.py, with every print replaced by the level it deserved.

    Note what changed besides the function name. Each line now carries a
    severity, so an operator can ask for INFO and above and never see the
    per-record chatter. The result of the function is RETURNED rather than
    printed, so the log and the output are two different streams. And the
    API key does not appear at all, because it was never the log's business.
    """
    log.info("preparation starting: %d records", len(records))
    kept = []
    for record in records:
        log.debug("processing record %s", record["id"])
        if not record["text"]:
            log.warning("skipping record %s: empty text", record["id"])
            continue
        if record["label"] not in VALID_LABELS:
            log.warning("skipping record %s: unknown label %r", record["id"], record["label"])
            continue
        kept.append(record)
    log.info("preparation done: kept %d of %d", len(kept), len(records))
    return kept


def demo_a() -> None:
    banner("A", "The same job, converted: severity, and a result you can pipe")
    log = fresh_logger("prep")
    log.setLevel(logging.DEBUG)
    log.propagate = False

    everything = attach_buffer(log, logging.DEBUG)
    prepare(RECORDS, log)
    show(everything, "the developer's view: handler at DEBUG")

    log = fresh_logger("prep")
    log.setLevel(logging.DEBUG)
    log.propagate = False
    operator = attach_buffer(log, logging.INFO)
    kept = prepare(RECORDS, log)
    show(operator, "the operator's view: SAME CODE, handler at INFO")

    print()
    print("The two views came from one unchanged function. That is the whole")
    print("difference from print(): the decision about what is worth seeing")
    print("moved out of the call site and into configuration.")
    print(f"(the function returned {len(kept)} records, which never touched the log)")


# ---------------------------------------------------------------------------
# B. The two-level trap
# ---------------------------------------------------------------------------


def demo_b() -> None:
    banner("B", "The two-level trap: the message that vanishes")
    log = fresh_logger("trap")
    log.setLevel(logging.DEBUG)          # the logger will accept DEBUG
    log.propagate = False
    stream = attach_buffer(log, logging.WARNING)  # the handler will not emit it

    log.debug("this debug line is accepted by the logger and dropped by the handler")
    log.info("so is this info line")
    log.warning("this warning gets through")

    print("logger level:  DEBUG   (logging.getLogger('trap').level ->",
          logging.getLevelName(log.level) + ")")
    print("handler level: WARNING (log.handlers[0].level ->",
          logging.getLevelName(log.handlers[0].level) + ")")
    show(stream, "three calls were made; this is what came out")
    print()
    print("A record has to pass TWO level checks, and they belong to two")
    print("different objects. The logger's check happens first and decides")
    print("whether a LogRecord is created at all. Each handler then applies")
    print("its own. Setting the logger to DEBUG and wondering where your")
    print("debug output went is the single most common logging question")
    print("there is, and this is the whole answer.")

    log.handlers.clear()
    stream2 = attach_buffer(log, logging.DEBUG)
    log.debug("and now, with a handler that accepts DEBUG")
    show(stream2, "the fix: lower the HANDLER's level too")


# ---------------------------------------------------------------------------
# C. Propagation and the duplicate message
# ---------------------------------------------------------------------------


def _propagation_setup(propagate: bool, app_handler: bool):
    """Build root + myapp + myapp.loader from scratch, and return the buffers."""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG)
    root_stream = attach_buffer(root, logging.DEBUG, "ROOT     | %(name)s | %(message)s")

    app = fresh_logger("myapp")
    app.setLevel(logging.DEBUG)
    app.propagate = propagate
    app_stream = io.StringIO()
    if app_handler:
        app_stream = attach_buffer(app, logging.DEBUG, "MYAPP    | %(name)s | %(message)s")

    child = logging.getLogger("myapp.loader")
    child.handlers.clear()
    child.filters.clear()
    child.setLevel(logging.NOTSET)
    child.propagate = True
    return child, app_stream, root_stream


def demo_c() -> None:
    banner("C", "Propagation: why you are seeing everything twice")

    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level

    child, app_stream, root_stream = _propagation_setup(propagate=True, app_handler=True)
    child.info("loaded 3 files")

    print("Handlers: one on the root logger, one on 'myapp'. One call, made")
    print("on 'myapp.loader'.")
    show(app_stream, "what the myapp handler wrote")
    show(root_stream, "what the root handler wrote")
    print()
    print("Two lines for one call. A record travels UP the dotted hierarchy —")
    print("myapp.loader, then myapp, then root — and every handler it passes")
    print("emits it. The ancestors' LEVELS are not consulted on the way up,")
    print("only their handlers. That is deliberate and it is why the duplicate")
    print("surprises people.")
    print()
    print("The usual cause is logging.basicConfig(), which quietly puts a")
    print("handler on the ROOT logger. Add one of your own and you now have")
    print("two.")

    # Fix 1: stop the record travelling any further up than myapp.
    child, app_stream, root_stream = _propagation_setup(propagate=False, app_handler=True)
    child.info("loaded 3 files")
    show(app_stream, "fix 1: myapp.propagate = False — myapp handler")
    show(root_stream, "fix 1: myapp.propagate = False — root handler")

    # Fix 2: the better one for an application — configure ONE place.
    child, app_stream, root_stream = _propagation_setup(propagate=True, app_handler=False)
    child.info("loaded 3 files")
    show(app_stream, "fix 2: handlers in ONE place only — myapp handler")
    show(root_stream, "fix 2: handlers in ONE place only — root handler")
    print()
    print("Both fixes work and they are not equivalent. propagate = False is")
    print("the right answer for a LIBRARY that must not have its records")
    print("escape into an application it knows nothing about. 'configure one")
    print("place' is the right answer for an APPLICATION, because the")
    print("alternative is a tree of loggers each with an opinion about where")
    print("its output goes, and no single place to change it.")

    root.handlers.clear()
    root.handlers.extend(saved_handlers)
    root.setLevel(saved_level)


# ---------------------------------------------------------------------------
# D. exception() against error(str(e))
# ---------------------------------------------------------------------------


def parse_batch_size(text: str) -> int:
    return int(text)


def demo_d() -> None:
    banner("D", "exception() against error(str(e)): the traceback is the value")

    log = fresh_logger("parse")
    log.setLevel(logging.DEBUG)
    log.propagate = False
    poor = attach_buffer(log, logging.DEBUG, "%(levelname)-8s %(message)s")

    try:
        parse_batch_size("sixty-four")
    except ValueError as error:
        log.error("could not parse batch size: %s", str(error))
    show(poor, "log.error(str(e)) — what the on-call engineer receives")

    log.handlers.clear()
    good = attach_buffer(log, logging.DEBUG, "%(levelname)-8s %(message)s")
    try:
        parse_batch_size("sixty-four")
    except ValueError:
        # Inside an except block, exception() is error() plus exc_info=True.
        # It reads the exception currently being handled out of the
        # interpreter, so you do not pass it anything.
        log.exception("could not parse batch size")
    text = good.getvalue().replace(str(LAB_DIR), "<lab>")
    print("--- log.exception() — the same failure ---")
    print(text.rstrip())
    print()
    print("The first version says a value was bad. The second says WHICH LINE")
    print("of WHICH FUNCTION was called with it, and by whom. On a machine you")
    print("cannot attach a debugger to, that difference is the difference")
    print("between a fix and a guess.")
    print()
    print("str(e) also loses the exception's TYPE. 'invalid literal for int()")
    print("with base 10' happens to name it; plenty of exceptions have empty")
    print("messages and str(e) then logs an empty string.")


# ---------------------------------------------------------------------------
# E. Lazy formatting
# ---------------------------------------------------------------------------


class ExpensiveToRender:
    """Counts how many times something asked for its string form."""

    renders = 0

    def __str__(self) -> str:
        ExpensiveToRender.renders += 1
        return "a summary that cost real work to produce"


def demo_e() -> None:
    banner("E", "Lazy formatting: log.info('saw %s', x) rather than an f-string")

    log = fresh_logger("lazy")
    log.setLevel(logging.INFO)          # DEBUG will be rejected by the logger
    log.propagate = False
    attach_buffer(log, logging.INFO)

    ExpensiveToRender.renders = 0
    for _ in range(1000):
        log.debug("summary: %s", ExpensiveToRender())     # lazy
    lazy_renders = ExpensiveToRender.renders

    ExpensiveToRender.renders = 0
    for _ in range(1000):
        log.debug(f"summary: {ExpensiveToRender()}")      # eager
    eager_renders = ExpensiveToRender.renders

    print(f"1000 suppressed DEBUG calls with %s formatting: {lazy_renders} renders")
    print(f"1000 suppressed DEBUG calls with an f-string:   {eager_renders} renders")
    print()
    print("The f-string is evaluated BEFORE logging is called, because that is")
    print("what an argument is. The %s form hands logging the object and the")
    print("template separately, and logging only joins them if a handler is")
    print("actually going to emit the record.")
    print()
    print("What it saves is therefore exactly this: the cost of rendering")
    print("arguments for records nobody wanted. On a hot path with expensive")
    print("reprs — a dataframe, a model, a large dict — that is the whole cost")
    print("of the logging call. On a cheap int it is nearly nothing, and the")
    print("honest reason to use %s everywhere is consistency plus one more")
    print("thing: the unformatted template survives onto the record as")
    print("record.msg, so a structured backend can group every occurrence of")
    print("'summary: %s' as one event with different arguments.")


# ---------------------------------------------------------------------------
# F. The five levels
# ---------------------------------------------------------------------------


def demo_f() -> None:
    banner("F", "The five levels, chosen honestly")
    log = fresh_logger("levels")
    log.setLevel(logging.DEBUG)
    log.propagate = False
    stream = attach_buffer(log, logging.DEBUG, "%(levelname)-8s (%(levelno)3d)  %(message)s")

    log.debug("retrieved 128 rows from the cache in one query")
    log.info("run 4711 started: model=small-encoder data=2026-08-01 seed=7")
    log.warning("upstream returned 429; retrying in 2s (attempt 2 of 5)")
    log.error("could not write the output file; this batch produced nothing")
    log.critical("no disk space remains; shutting down")
    show(stream, "one line at each level, with its numeric value")
    print()
    print("The question that decides the level is not 'how alarming does this")
    print("feel' but 'who is this for, and what do they do about it':")
    print()
    print("  DEBUG    for the developer, tracing their own code. Off in")
    print("           production, on when you are hunting something.")
    print("  INFO     for the operator: the run started, the run finished,")
    print("           this many records. Normal life, worth recording.")
    print("  WARNING  surprising but survivable. The retry worked. The")
    print("           deprecated flag was used. Nobody has to get up.")
    print("  ERROR    work that did not happen. This batch produced nothing.")
    print("           Somebody has to look, though not necessarily now.")
    print("  CRITICAL the process is going down and will stop doing its job.")
    print()
    print("The failure mode to avoid is level inflation. If routine events are")
    print("logged as WARNING, the warnings stop being read, and the real one")
    print("is invisible in the noise. A level is a promise to the reader about")
    print("what it costs them to ignore the line.")


def main() -> None:
    demo_a()
    demo_b()
    demo_c()
    demo_d()
    demo_e()
    demo_f()
    print()
    print("=" * 70)
    print("Six demonstrations complete.")


if __name__ == "__main__":
    main()
