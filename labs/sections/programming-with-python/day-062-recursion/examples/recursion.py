#!/usr/bin/env python3
"""recursion.py — worked examples of recursion, as a small CLI.

Every subcommand demonstrates one recursive function so you can watch the
base case and the recursive case do their work on real input:

    factorial  n! by recursion (the "hello world" of recursion)
    sum        add a flat list of numbers by recursion
    flatten    turn an arbitrarily nested list into one flat list
    treesum    add every number in a nested dict/list (a tree walk)
    fib        Fibonacci — naive recursion vs an lru_cache-memoized version,
               reporting call counts so the exponential blow-up is visible

Input comes entirely from command-line arguments (never an interactive
prompt), so the tool can be tested and automated without a human. The nested
data for `flatten` and `treesum` is passed as JSON, which maps cleanly onto
Python lists and dicts.

    python3 recursion.py factorial --n 5
    python3 recursion.py sum --values 1,2,3,4,5
    python3 recursion.py flatten --data "[1, [2, [3, 4]], 5]"
    python3 recursion.py treesum --data '{"a": 1, "b": {"c": 2, "d": [3, 4]}}'
    python3 recursion.py fib --n 30
"""
import argparse
import json
import sys
from functools import lru_cache


def factorial(n):
    """Return n! by recursion.

    Base case: 0! and 1! are 1. Recursive case: n! = n * (n - 1)!. Each call
    shrinks n toward the base case, so the recursion is guaranteed to stop.
    """
    if n < 0:
        raise ValueError("factorial is undefined for negative numbers")
    if n <= 1:                      # base case — stop here, no further calls
        return 1
    return n * factorial(n - 1)     # recursive case — a smaller subproblem


def list_sum(numbers):
    """Return the sum of a flat list by recursion.

    Base case: the empty list sums to 0. Recursive case: the sum is the first
    element plus the sum of the rest. Each call works on a shorter list.
    """
    if not numbers:                 # base case — nothing left to add
        return 0
    return numbers[0] + list_sum(numbers[1:])   # recursive case


def flatten(items):
    """Return a single flat list from an arbitrarily nested list.

    This is a problem recursion suits perfectly: the structure is nested to
    an unknown depth, and the function calls itself on each sublist until it
    reaches plain (non-list) values, which are the base case.
    """
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten(item))   # recursive case — dive into the sublist
        else:
            result.append(item)            # base case — a leaf value
    return result


def tree_sum(node):
    """Add every number reachable inside a nested dict/list tree.

    A node is a number (a leaf), a list, or a dict. Numbers are the base
    case; lists and dicts are the recursive case — sum the results of walking
    each child. Anything else (strings, None) contributes 0.
    """
    if isinstance(node, bool):
        return 0                                  # bool is a subclass of int; ignore
    if isinstance(node, (int, float)):
        return node                               # base case — a numeric leaf
    if isinstance(node, list):
        return sum(tree_sum(child) for child in node)          # recurse over items
    if isinstance(node, dict):
        return sum(tree_sum(value) for value in node.values())  # recurse over values
    return 0                                      # strings, None, etc.


def fib_naive(n, counter):
    """Return the nth Fibonacci number by naive tree recursion.

    counter is a one-element list used to count how many times this function
    is called, so we can measure the exponential explosion. Each call spawns
    two more (for n >= 2), which is why naive Fibonacci is so wasteful.
    """
    counter[0] += 1
    if n < 2:                       # base cases: fib(0) = 0, fib(1) = 1
        return n
    return fib_naive(n - 1, counter) + fib_naive(n - 2, counter)


def make_memoized_fib():
    """Return an lru_cache-memoized Fibonacci function.

    lru_cache remembers each fib(n) the first time it is computed, so every
    later request for the same n is a cache hit instead of a re-computation.
    That turns the exponential tree into a linear number of computations.
    """
    @lru_cache(maxsize=None)
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)
    return fib


def cmd_factorial(args):
    """factorial: print n! computed by recursion."""
    result = factorial(args.n)
    print(f"factorial({args.n}) = {result}")
    return 0


def cmd_sum(args):
    """sum: parse a comma-separated list of ints and add it by recursion."""
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
    """Parse text as JSON and confirm its top-level type, or raise ValueError."""
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
    """flatten: parse a nested JSON list and print it flattened by recursion."""
    nested = _load_json(args.data, expect="list")
    print(f"flatten -> {flatten(nested)}")
    return 0


def cmd_treesum(args):
    """treesum: parse a nested JSON tree and print the sum of its numbers."""
    tree = _load_json(args.data, expect="tree")
    print(f"treesum -> {tree_sum(tree)}")
    return 0


def cmd_fib(args):
    """fib: compute fib(n) two ways and report the call counts.

    The naive version counts every call; the memoized version reports its
    cache statistics. The contrast is the whole point: memoization collapses
    an exponential number of calls into a linear number of computations.
    """
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
    """Build the argparse parser: five subcommands, one per recursive idea."""
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
    """Entry point: parse arguments, dispatch, and turn a ValueError into
    a clear message plus exit code 1."""
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
