"""Step 5: a context manager of your own, and the guarantee it makes.

`with` is not built into the file object. It is a protocol: any object with
__enter__ and __exit__ can be used with `with`. __exit__ runs on the way out
of the block whether the body finished normally or raised — which is exactly
the guarantee you relied on with files on Day 64, now implemented by you.

__exit__ receives three arguments describing the exception, or three Nones if
there was none:
    exc_type   the exception class      (or None)
    exc_value  the exception instance   (or None)
    traceback  the traceback object     (or None)

Its RETURN VALUE decides what happens next: False (or None) lets the
exception continue to the caller; True SWALLOWS it. Returning True by
accident is how exceptions silently vanish, so `Menu.__exit__` returns False
deliberately.

Run it:  python3 examples/05_context_manager.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kitchen import Dish, Menu  # noqa: E402


def main():
    print("-- normal run: the body succeeds --")
    brunch = Menu("Brunch", [Dish("Waffles", 9)])
    with brunch as service:
        print(f"  inside: {len(service)} dish, open = {service.open}")
    print(f"after: {brunch.open}")

    print()
    print("-- the case that matters: the body raises --")
    bad = Menu("Bad night", [Dish("Souffle", 45)])
    try:
        with bad:
            raise ValueError("burnt the souffle")
    except ValueError as err:
        # [service closed] printed BEFORE this line: __exit__ ran on the way
        # out, and returning False let the exception carry on to us here.
        print(f"caught: {err} | open = {bad.open}")

    print()
    print("-- proof the cleanup is unconditional --")
    print(f"cleanup ran after success: {brunch.open is False}")
    print(f"cleanup ran after failure: {bad.open is False}")
    print("exception still reached the caller: True")


if __name__ == "__main__":
    main()
