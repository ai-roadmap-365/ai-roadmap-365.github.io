# Requirements — Day 096

## What you need

| Tool | Minimum | Used on the authoring machine | Why the minimum is what it is |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | `asyncio.TaskGroup`, `asyncio.timeout` and `except*` all arrived in 3.11. Earlier versions raise a `SyntaxError` on `except*` |
| `bash` | 3.2 | 3.2.57 | `tests/run_tests.sh` and `starter/02_check.sh`. Written for bash 3.2 so the macOS system bash works unmodified |

Two or more logical CPUs. The machine used here had 14.

## What you do not need

`requirements.txt` in this directory lists no packages, and that is
deliberate rather than an oversight. Every concurrency model this lab
compares ships with Python:

| Model | Module | In the standard library since |
| --- | --- | --- |
| Threads | `threading` | Long enough that the documentation no longer records a version; it predates every other row here |
| Processes | `multiprocessing` | Python 2.6, 2008 |
| Uniform pool interface | `concurrent.futures` | Python 3.2, 2011 |
| Event loop and coroutines | `asyncio` | Python 3.4, 2014 |
| `async` / `await` syntax | language | Python 3.5, 2015 |
| Structured concurrency | `asyncio.TaskGroup` | Python 3.11, 2022 |

Also used, all standard library: `queue`, `time`, `urllib.request`,
`urllib.parse`, `http.server`, `socket` (indirectly, through `asyncio` and
`http.server`), `collections`, `statistics`, `sysconfig`, `importlib.util`,
`contextlib`, `pathlib`, `ast`.

`tests/run_tests.sh` parses every import in every `.py` file in this lab
against `sys.stdlib_module_names` and fails if anything outside it appears.
So this claim is checked on each run rather than asserted here.

## The libraries this lab talks about but does not install

The lesson's Alternatives section covers `trio`, `anyio`, `gevent` and
Celery. None of them is installed, none is imported, and **no output from any
of them is reproduced anywhere in this lab or lesson** — they are described
from their documentation and labelled as such. If you want to try them, they
belong in a virtual environment of your own, outside this directory.

## How the workload sizes were chosen

Both are calibrated, and the reasoning matters because a badly sized workload
makes a measurement lie.

**Waiting work** — 20 requests at 0.100 s each. The delay is a `time.sleep`
inside the fixture server, so it is exact and identical on every machine. It
is long enough that the waiting dominates the per-request overhead of urllib
and of opening a socket, and short enough that the sequential baseline
finishes in about two seconds. The result is a sequential run pinned near
2.0 s on any hardware, which is what makes the ratios comparable across
machines.

**Computing work** — 4 tasks, each counting the primes below 500,000 by
trial division, measured on the authoring machine at 0.364 s per call. The
full calibration, captured from the command below:

| Limit | Primes below it | Time on the authoring machine |
| --- | --- | --- |
| 120,000 | 11,301 | 0.046 s |
| 400,000 | 33,860 | 0.260 s |
| 500,000 | 41,538 | 0.364 s |
| 700,000 | 56,543 | 0.594 s |
| 1,000,000 | 78,498 | 1.014 s |

500,000 was chosen as the smallest size that is comfortably larger than the
cost of starting a process pool — on macOS, `ProcessPoolExecutor` uses the
spawn start method, so each of the four children re-imports the module before
doing any work. Too small a task and that start-up cost is the entire
measurement; too large and the test suite becomes tedious to run.

Trial division was chosen over a sieve on purpose: it is a tight arithmetic
loop in pure Python that holds the interpreter lock, which is precisely the
shape of work the comparison is about. A sieve would spend much of its time
in list operations and would muddy the result.

The starter checker uses 400,000 rather than 500,000, and 12 requests rather
than 20, so that a learner re-running it after every edit is not waiting
around.

## Reproducing the calibration

```bash
python3 - <<'PY'
import sys, time
sys.path.insert(0, "examples")
import labkit
for limit in (120_000, 400_000, 500_000, 700_000, 1_000_000):
    start = time.perf_counter()
    count = labkit.count_primes(limit)
    print(f"{limit:>9,}  {count:>7,} primes  {time.perf_counter() - start:.3f}s")
PY
```

Run it from the lab directory. Your times will differ; the prime counts will
not, and are checkable against any table of the prime-counting function.

## What is deliberately absent

- **No `pytest`.** The harness is a bash assert script, as everywhere else in
  this course, so the lab has no dependency at all.
- **No benchmarking library.** `time.perf_counter` and three repetitions with
  the spread printed is the right amount of machinery for teaching the shape
  of a result. A serious benchmark of a serious system needs more, and the
  lesson says so rather than pretending three runs is rigorous.
- **No async HTTP client.** There is none in the standard library. The lab
  writes twelve lines of raw `asyncio.open_connection` instead, which is more
  instructive than importing one would have been: you can see exactly which
  three lines are the `await` points.
