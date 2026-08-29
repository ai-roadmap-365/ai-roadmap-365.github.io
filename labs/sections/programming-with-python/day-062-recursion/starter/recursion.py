#!/usr/bin/env python3
"""recursion.py — YOUR working file.

Build these recursive functions one exercise at a time. Each numbered
exercise names exactly what to write, including the base case and the
recursive case. The finished reference is in examples/recursion.py — try each
exercise yourself before peeking.

When all five exercises are done, this file behaves like the reference:

    python3 starter/recursion.py factorial --n 5
    python3 starter/recursion.py sum --values 1,2,3,4,5
    python3 starter/recursion.py flatten --data "[1, [2, [3, 4]], 5]"
    python3 starter/recursion.py treesum --data '{"a": 1, "b": [2, 3]}'
    python3 starter/recursion.py fib --n 30

Then run:  bash tests/run_tests.sh
"""
import argparse
import json
import sys
from functools import lru_cache


def factorial(n):
    """Return n! by recursion."""
    # Exercise 1: FACTORIAL.
    # 1. If n < 0, raise ValueError("factorial is undefined for negative numbers").
    # 2. BASE CASE: if n <= 1, return 1 (0! and 1! are both 1). This stops
    #    the recursion — without it the calls never end.
    # 3. RECURSIVE CASE: return n * factorial(n - 1). Each call shrinks n
    #    toward the base case.
    raise NotImplementedError("Exercise 1: implement factorial")


def list_sum(numbers):
    """Return the sum of a flat list by recursion."""
    # Exercise 2: RECURSIVE LIST SUM.
    # 1. BASE CASE: an empty list sums to 0 — `if not numbers: return 0`.
    # 2. RECURSIVE CASE: return numbers[0] + list_sum(numbers[1:]).
    #    Each call works on a shorter list (the "rest").
    raise NotImplementedError("Exercise 2: implement list_sum")


def flatten(items):
    """Return a single flat list from an arbitrarily nested list."""
    # Exercise 3: FLATTEN A NESTED LIST.
    # 1. Make an empty result list.
    # 2. For each item: if it is a list (isinstance(item, list)), it is the
    #    RECURSIVE CASE — extend result with flatten(item). Otherwise it is a
    #    leaf (the BASE CASE) — append it.
    # 3. Return result.
    raise NotImplementedError("Exercise 3: implement flatten")


def tree_sum(node):
    """Add every number reachable inside a nested dict/list tree."""
    # Exercise 4: WALK A NESTED TREE.
    # A node is a number (leaf), a list, or a dict. Handle each:
    # 1. `if isinstance(node, bool): return 0`  (bool is a subclass of int)
    # 2. BASE CASE: `if isinstance(node, (int, float)): return node`
    # 3. RECURSIVE CASE (list): return sum(tree_sum(child) for child in node)
    # 4. RECURSIVE CASE (dict): return sum(tree_sum(v) for v in node.values())
    # 5. Anything else (strings, None): return 0
    raise NotImplementedError("Exercise 4: implement tree_sum")


def fib_naive(n, counter):
    """Return fib(n) by naive tree recursion, counting every call."""
    # Exercise 5: NAIVE FIBONACCI (tree recursion).
    # 1. Increment the call counter: counter[0] += 1  (already written below;
    #    keep it first so every call is counted).
    # 2. BASE CASES: if n < 2, return n  (fib(0) = 0, fib(1) = 1).
    # 3. RECURSIVE CASE: return fib_naive(n - 1, counter) + fib_naive(n - 2, counter).
    #    Notice each call makes TWO more — that is why this is exponential.
    counter[0] += 1
    raise NotImplementedError("Exercise 5: implement fib_naive")


def make_memoized_fib():
    """Return an lru_cache-memoized Fibonacci function. (Provided.)

    lru_cache remembers each fib(n) the first time it is computed, so later
    requests for the same n are cache hits instead of re-computations. That
    turns the exponential tree into a linear number of computations.
    """
    @lru_cache(maxsize=None)
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)
    return fib


def cmd_factorial(args):
    """factorial: print n! computed by recursion. (Provided.)"""
    print(f"factorial({args.n}) = {factorial(args.n)}")
    return 0


def cmd_sum(args):
    """sum: parse a comma-separated list and add it by recursion. (Provided.)"""
    text = args.values.strip()
    if not text:
        numbers = []
    else:
        try:
            numbers = [int(piece) for piece in text.split(",")]
        except ValueError:
            raise ValueError(f"--values must be comma-separated integers, got {args.values!r}")
    print(f"sum({numbers}) = {list_sum(numbers)}")
    return 0


def _load_json(text, expect):
    """Parse text as JSON and confirm its top-level type. (Provided.)"""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(f"--data is not valid JSON ({err})")
    if expect == "list" and not isinstance(data, list):
        raise ValueError("--data must be a JSON list, e.g. [1, [2, 3]]")
    if expect == "tree" and not isinstance(data, (list, dict)):
        raise ValueError("--data must be a JSON object or list")
    return data


def cmd_flatten(args):
    """flatten: parse a nested JSON list and print it flattened. (Provided.)"""
    print(f"flatten -> {flatten(_load_json(args.data, expect='list'))}")
    return 0


def cmd_treesum(args):
    """treesum: parse a nested JSON tree and print the sum of its numbers. (Provided.)"""
    print(f"treesum -> {tree_sum(_load_json(args.data, expect='tree'))}")
    return 0


def cmd_fib(args):
    """fib: compute fib(n) two ways and report the call counts. (Provided.)"""
    n = args.n
    counter = [0]
    naive_value = fib_naive(n, counter)
    naive_calls = counter[0]

    fib = make_memoized_fib()
    memo_value = fib(n)
    info = fib.cache_info()

    assert naive_value == memo_value, "the two methods must agree"
    print(f"fib({n}) = {memo_value}")
    print(f"naive recursion: {naive_calls} calls")
    print(f"memoized (lru_cache): {info.misses} computations, {info.hits} cache hits")
    ratio = naive_calls // max(info.misses, 1)
    print(f"the naive version made {ratio}x more calls than the memoized version computed")
    return 0


def build_parser():
    """Build the argparse parser: five subcommands, one per idea. (Provided.)"""
    parser = argparse.ArgumentParser(
        prog="recursion.py",
        description="Worked examples of recursion: factorial, sum, flatten, treesum, fib.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="{factorial,sum,flatten,treesum,fib}",
    )

    fac = subparsers.add_parser("factorial", help="compute n! by recursion")
    fac.add_argument("--n", type=int, required=True, help="a non-negative integer")
    fac.set_defaults(func=cmd_factorial)

    add = subparsers.add_parser("sum", help="add a comma-separated list by recursion")
    add.add_argument("--values", required=True, help="e.g. 1,2,3,4")
    add.set_defaults(func=cmd_sum)

    flat = subparsers.add_parser("flatten", help="flatten a nested JSON list")
    flat.add_argument("--data", required=True, help='e.g. "[1, [2, [3, 4]], 5]"')
    flat.set_defaults(func=cmd_flatten)

    tree = subparsers.add_parser("treesum", help="sum every number in a nested JSON tree")
    tree.add_argument("--data", required=True, help='e.g. \'{"a": 1, "b": [2, 3]}\'')
    tree.set_defaults(func=cmd_treesum)

    fib = subparsers.add_parser("fib", help="Fibonacci: naive vs lru_cache memoized")
    fib.add_argument("--n", type=int, required=True, help="which Fibonacci number")
    fib.set_defaults(func=cmd_fib)

    return parser


def main(argv):
    """Entry point: parse arguments, dispatch, and turn errors into exit 1. (Provided.)"""
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        return args.func(args)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    except RecursionError:
        print(
            "error: maximum recursion depth exceeded — the input is too deeply "
            "nested for the default limit (see sys.setrecursionlimit)",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
