"""summary_core.py — YOUR working file: the functional core.

The design is already done for you: the module is split into a pure core
(this file) and a thin imperative shell (summary.py, provided complete).
The three functions below are the whole core, and their docstrings — the
signatures and contracts — are written first, on purpose. That is
docstring-driven design: decide what each function promises before you
write a line of its body. Your job is to fill in the bodies so each
function keeps the promise its docstring makes.

Every function here must stay PURE: no print(), no input(), no open(),
no reading argv — just values in and values out. All of that I/O belongs
in summary.py. Purity is why tests/run_tests.sh can check this core with
plain function calls.

Finish the three numbered exercises, then run:  bash tests/run_tests.sh
"""


def parse_numbers(text):
    """Parse free-form text into a list of floats.

    Tokens may be separated by commas, spaces, tabs, or newlines. Empty
    or blank text yields an empty list. A token that is not a number
    raises ValueError naming the offending token.

    >>> parse_numbers("1, 2, 3")
    [1.0, 2.0, 3.0]
    >>> parse_numbers("")
    []
    """
    # Exercise 1: PARSE (a pure boundary check).
    # 1. Turn every comma into a space, then .split() to get tokens.
    # 2. For each token, try float(token) and collect the result.
    # 3. If float(token) raises ValueError, raise ValueError(f"{token!r} is
    #    not a number") so the caller learns which token was bad.
    # 4. Return the list of floats ([] when there are no tokens).
    raise NotImplementedError("Exercise 1: implement parse_numbers")


def summarize(numbers):
    """Return summary statistics for a non-empty list of numbers.

    Returns a dict with keys count, total, mean, minimum, maximum, and
    above_mean (how many values are strictly greater than the mean).
    Raises ValueError if numbers is empty.
    """
    # Exercise 2: SUMMARIZE (pure computation).
    # 1. If numbers is empty, raise ValueError("cannot summarize an empty
    #    list of numbers"). An empty input is the caller's decision, not
    #    something the core should guess about.
    # 2. Compute count, total, mean (= total / count), minimum, maximum.
    # 3. Compute above_mean: how many values are strictly greater than mean.
    #    Hint: sum(1 for value in numbers if value > mean)
    # 4. Return them in a dict with exactly those six keys.
    raise NotImplementedError("Exercise 2: implement summarize")


def format_summary(summary):
    """Render a summary dict as an aligned block of human-readable text.

    Pure string-building: return the text, do not print it. The shell
    decides where the text goes; the tests check the returned string.
    Each of the six statistics goes on its own line. Format the four
    real-valued numbers (total, mean, minimum, maximum) to two decimals
    with :.2f; count and above_mean are plain integers.
    """
    # Exercise 3: FORMAT (pure rendering).
    # Build and return a multi-line string. To match the reference and the
    # tests exactly, use these label widths and this order:
    #     count      <count>
    #     total      <total, 2 decimals>
    #     mean       <mean, 2 decimals>
    #     minimum    <minimum, 2 decimals>
    #     maximum    <maximum, 2 decimals>
    #     above mean <above_mean>
    # Hint: build a list of f-strings and "\n".join(...) them.
    raise NotImplementedError("Exercise 3: implement format_summary")
