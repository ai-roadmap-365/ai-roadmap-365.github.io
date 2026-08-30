# Troubleshooting — Day 324

## The demo takes 30 seconds instead of about 2.4

Your budget is not being enforced. `extract_pathological` sleeps for 30 seconds, and it will not stop on its own.

The common cause is trying to enforce the deadline with a thread. A thread cannot be killed, and `ThreadPoolExecutor` used as a context manager waits for its workers on exit — so `future.result(timeout=...)` returns but the `with` block then blocks for the full 30 seconds anyway. This lab's first version had exactly that bug. Use `extract_with_budget`, which runs the extractor in a child process and terminates it.

## Everything is accepted, including `doc-03.scan`

Your yield signal is a length rather than a ratio. A genuinely short document and a failed extraction of a long one both produce little text; only `len(text) / len(doc.data)` distinguishes them.

Check with:

```bash
python3 -c "
import sys; sys.path.insert(0,'examples')
from process import score, Document
print(score(Document('s',b'hi'),'hi').text_yield)          # near 1.0
print(score(Document('b',b'x'*1000),'hi').text_yield)      # near 0.0"
```

## `doc-04.bin` is accepted

Your alphabetic ratio counts every non-space character rather than only letters. `=?#` are not letters. Use `str.isalpha()`.

## `doc-07.xyz` raises instead of being dead-lettered

An unrecognised format is a normal outcome. Check `fmt not in EXTRACTORS` and return a `dead` Result with `f"no extractor for format '{fmt}'"` rather than raising or looking up a missing key.

## `test_detection_reads_content_not_the_extension` fails

You are branching on `doc.name`. Detection must look only at `doc.data`. `doc-03.scan` and `doc-06.slow` are named for formats that do not exist precisely to catch this.

## `ZeroDivisionError` in `score`

Empty extracted text is a common case, not an edge case — a scan can yield nothing at all. Guard every denominator, and return `0.0` rather than raising.

## The suite takes 17 seconds

Tests that do not care about the exact timeout should pass a smaller budget: `process_all(build_corpus(), budget_s=0.3)`. Only the test that asserts on timeout behaviour needs a realistic one.

## `RuntimeError` about the start method, or the demo hangs on Windows

`multiprocessing` needs the entry point guarded. `examples/process_demo.py` already has `if __name__ == "__main__":`; keep it if you write your own harness.

## `NotImplementedError` everywhere

Expected. The starter stubs `detect`, `score` and `process_one`, and every test depends on at least one of them — see `expected-output/starter-run.txt`.
