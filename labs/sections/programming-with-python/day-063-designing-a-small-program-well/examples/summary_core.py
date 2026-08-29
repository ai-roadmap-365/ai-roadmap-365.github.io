"""summary_core.py — the functional core of the summary tool.

Every function in this module is PURE: it takes values in and returns
values out, with no reading, no printing, no files, and no global state.
That purity is exactly what makes the core easy to test — you call a
function with an example and check what it returns, with no fake files
and no captured output. The messy work of reading arguments, opening
files, and printing lives in the imperative shell (summary.py), never
here. Keeping logic and I/O apart is the single design idea this program
exists to demonstrate.

The tool's job (its spec): turn free-form text full of numbers into a
small statistical summary — count, total, mean, minimum, maximum, and
how many values sit above the mean.
"""


def parse_numbers(text):
    """Parse free-form text into a list of floats.

    Tokens may be separated by commas, spaces, tabs, or newlines. Empty
    or blank text yields an empty list. A token that is not a number
    raises ValueError naming the offending token — the boundary check
    that keeps bad data out of the rest of the core.

    Args:
        text: the raw text to parse.

    Returns:
        A list of floats, one per token, in order.

    Raises:
        ValueError: if any token cannot be read as a number.
    """
    tokens = text.replace(",", " ").split()
    numbers = []
    for token in tokens:
        try:
            numbers.append(float(token))
        except ValueError:
            raise ValueError(f"{token!r} is not a number")
    return numbers


def summarize(numbers):
    """Return summary statistics for a non-empty list of numbers.

    Args:
        numbers: a list of numbers (floats or ints).

    Returns:
        A dict with keys count, total, mean, minimum, maximum, and
        above_mean (how many values are strictly greater than the mean).

    Raises:
        ValueError: if numbers is empty, because a summary of nothing has
            no meaning — the caller must decide what to do about it.
    """
    if not numbers:
        raise ValueError("cannot summarize an empty list of numbers")
    count = len(numbers)
    total = sum(numbers)
    mean = total / count
    above_mean = sum(1 for value in numbers if value > mean)
    return {
        "count": count,
        "total": total,
        "mean": mean,
        "minimum": min(numbers),
        "maximum": max(numbers),
        "above_mean": above_mean,
    }


def format_summary(summary):
    """Render a summary dict as an aligned block of human-readable text.

    This is pure string-building: it returns the text rather than
    printing it, so the shell decides where the text goes and the tests
    can check it directly.

    Args:
        summary: a dict as returned by summarize().

    Returns:
        A multi-line string, one statistic per line.
    """
    return "\n".join(
        [
            f"count      {summary['count']}",
            f"total      {summary['total']:.2f}",
            f"mean       {summary['mean']:.2f}",
            f"minimum    {summary['minimum']:.2f}",
            f"maximum    {summary['maximum']:.2f}",
            f"above mean {summary['above_mean']}",
        ]
    )
