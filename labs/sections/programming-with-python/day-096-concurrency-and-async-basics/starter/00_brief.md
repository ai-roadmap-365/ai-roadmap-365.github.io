# The brief — Waiting Versus Computing

Read this before you write anything. It takes three minutes and it is the
whole point of the day.

## The situation

You have inherited a small service. It does two things.

It **fetches** twenty records from an upstream system, one HTTP request each,
and each request takes about a tenth of a second because the upstream is slow.
And it **computes** a checksum over each batch, which is a few hundred
milliseconds of arithmetic per batch with no I/O at all.

Both are slow. Somebody suggests "make it concurrent". That instruction is
not actionable, because the right answer for the first half is the wrong
answer for the second half, and the wrong answer looks like it worked
because the code compiles, the tests pass and the timings do not move.

## The one question

Before you choose a tool, answer this about the work in front of you:

> **Is this work waiting, or is it computing?**

- **Waiting** — for a socket, a disk, a database, a lock, a subprocess, a
  human. The CPU is idle. Threads help. An event loop helps more, at the
  cost of every library in the call path having to cooperate.
- **Computing** — arithmetic, parsing, encoding, compression, model
  inference on the CPU. The CPU is busy. Threads do not help, because
  CPython lets only one thread execute Python bytecode at a time. Processes
  help, because each process has its own interpreter.

That is the decision. Everything else on this day is you proving it to
yourself rather than taking it on trust.

## What you are going to build

Eight functions in `starter/01_exercises.py`. Run
`bash starter/02_check.sh` at any point to see where you stand; it starts by
saying `0 of 8 exercises complete.` and names each one that is still open.

| # | Function | The point |
| --- | --- | --- |
| 1 | `fetch_all_sequentially` | The baseline. Everything is measured against it |
| 2 | `fetch_all_with_threads` | Waiting work + threads. Must be at least 2.5x faster |
| 3 | `fetch_all_with_asyncio` | Waiting work + event loop. Must be at least 2.5x faster |
| 4 | `count_primes_with_threads` | Computing work + threads. Correct, and **not** faster |
| 5 | `count_primes_with_processes` | Computing work + processes. Must be at least 1.4x faster |
| 6 | `wait_without_blocking_the_loop` | A blocking call rescued with `asyncio.to_thread` |
| 7 | `counter_that_loses_nothing` | A race the checker forces to happen, and your fix |
| 8 | `round_robin` | An event loop of your own, in about a dozen lines |

Exercise 4 is the one people skip because it looks like a repeat of exercise
2. It is the opposite of exercise 2, and the checker will print the ratio so
you can see it.

## What the requests actually talk to

Nothing outside your machine. `examples/labkit.py` starts a small HTTP
server bound to `127.0.0.1` on a port the operating system picks, and that
server sleeps for a fixed number of milliseconds before answering. So the
waiting is genuine — a real socket, a really blocked thread — and it is
also exactly reproducible, which the internet never is. Nothing in this lab
needs a network connection, a key or an account.

## How you will be judged

By behaviour and by ratios, never by a stopwatch reading. The checker asks
"is the threaded version at least two and a half times faster than the
sequential one on this machine, right now?" — never "did it finish in under
200 milliseconds". A millisecond figure is a fact about the machine that
produced it. A ratio is a fact about the program.

Hold yourself to the same rule when you report a performance result to
anybody: say what you measured, say how many times you ran it, say what the
spread was, and say which machine on which day.

## The order to work in

1. Exercise 1, then 2, then 3, and **look at the ratios** the checker prints.
2. Exercise 4, then 5, and look at those ratios too. This is the lesson.
3. Exercise 6 — the mistake that makes an async service serve one request at
   a time while looking busy.
4. Exercise 7 — shared state. Read `examples/04_race.py` afterwards, because
   it contains a result that contradicts what most books say about this, and
   the reason it does is worth knowing.
5. Exercise 8 — write the loop. After this, `await` is not magic.

Then run the six example scripts in order and read them. They are the
narrated version of everything you just did, with the measurements printed.
