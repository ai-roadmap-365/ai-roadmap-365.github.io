"""Exercise 1 -- fourteen functions to write.

Every function below has a working signature, a docstring saying exactly what
it must do, and a `return None` where your code goes. Returning None is how
the test suite knows you have not attempted it yet: `pytest starter -q` will
SKIP an unattempted function rather than fail it, so your score only ever
counts work you have actually done.

Check yourself as you go:

    .venv/bin/pytest starter -q

Nothing here needs NumPy and nothing here needs the network. `math` is the
only import you should need.
"""

import math
from typing import Callable, Iterable, Sequence

Scalar = Callable[[float], float]


# --------------------------------------------------------------------------
# 1.1 -- the two building blocks
# --------------------------------------------------------------------------


def product(factors: Iterable[float]) -> float:
    """Multiply an iterable of numbers together and return the result.

    An empty iterable must give 1.0, not 0.0. One is the identity for
    multiplication, and it is also the honest answer to "how much does x
    change per unit of x" when nothing happens in between.

    >>> product([2.0, 3.0])
    6.0

    Approach: start a running total at 1.0 and multiply each factor into it.
    """
    return None


def gear_ratio(ratios: Iterable[float]) -> float:
    """The overall ratio of a gear train: every stage ratio multiplied.

    If gear A turns twice per turn of B, and B turns three times per turn of
    C, then A turns six times per turn of C.

    Approach: this is one line, and it calls `product`.
    """
    return None


# --------------------------------------------------------------------------
# 1.2 -- the measuring instruments, carried over from Days 108 and 109
# --------------------------------------------------------------------------


def central_difference(f: Scalar, x: float, h: float) -> float:
    """Estimate f'(x) as (f(x + h) - f(x - h)) / (2h).

    Raise `ValueError` if h is zero or negative -- a step of zero would
    divide by zero, and a negative step is almost certainly a typo rather
    than an intention.

    This is the tool that checks everything else in the lab, and it must know
    nothing about the chain rule for that check to mean anything.

    Approach: guard the step, then one subtraction over 2h. Note the
    denominator is 2h and not h; dividing by h is the most common way to get
    this exactly half right.
    """
    return None


def partial_difference(
    f: Callable[..., float], point: Sequence[float], index: int, h: float
) -> float:
    """Estimate one partial derivative of a function of several inputs.

    Nudge coordinate `index` by +h and by -h, hold every other coordinate
    still, and divide the difference by 2h. Raise `ValueError` on a
    non-positive h, as above.

    `f` is called as `f(*coordinates)`, so a two-input function is called
    `f(s, t)`.

    Approach: make two copies of `point` as lists, change one entry in each,
    and call f with each copy unpacked.
    """
    return None


# --------------------------------------------------------------------------
# 1.3 -- composition and the one-variable chain rule
# --------------------------------------------------------------------------


def compose(outer: Scalar, inner: Scalar) -> Scalar:
    """Return the FUNCTION x -> outer(inner(x)).

    Note that this returns a function, not a number. `inner` runs first even
    though it is written second.

    Approach: define a small function inside this one and return it.
    """
    return None


def chain_rule(
    d_outer: Scalar, inner: Scalar, d_inner: Scalar, x: float
) -> float:
    """The chain rule for one variable: dy/dx = dy/du x du/dx.

    The trap is in one word: the outer derivative is evaluated **at the inner
    value**, not at x. Compute u = inner(x) first, then multiply d_outer(u)
    by d_inner(x).

    With outer f(u) = u squared, inner g(x) = 3x + 1 and x = 2, the answer is
    2 x 7 x 3 = 42. If you get 12, you evaluated the outer derivative at x.

    Approach: two lines. Do not try to make it one.
    """
    return None


# --------------------------------------------------------------------------
# 1.4 -- chains of any depth
# --------------------------------------------------------------------------


def chain_values(stages: Sequence[Scalar], x: float) -> list[float]:
    """The forward pass: the input, then the output of each stage in turn.

    For n stages this returns n + 1 numbers, starting with x itself. Keeping
    x in the list means entry i is always the value that ARRIVES at stage i,
    which is what the next function needs.

    With the five stages in `dataset.FIVE_STAGES` starting from 1.0 the
    answer begins 1.0, 2.0, 5.0, 25.0, 5.0, ...

    Approach: a list starting with [x], then a loop that applies each stage
    to the running value and appends it.
    """
    return None


def chain_local_rates(
    stages: Sequence[Scalar], rates: Sequence[Scalar], x: float
) -> list[float]:
    """The local derivative of every stage, each evaluated at its own input.

    Raise `ValueError` if `stages` and `rates` are different lengths -- a
    chain with a missing derivative should be refused rather than silently
    truncated.

    For the five stages this gives 2.0, 1.0, 10.0, 0.1, 0.2. Stage 3's
    derivative is 2u and the u it sees is 5, so its rate is 10 -- not 2, and
    not anything computed at x.

    Approach: call `chain_values` first, then evaluate rate i at values[i].
    """
    return None


def chain_derivative(
    stages: Sequence[Scalar], rates: Sequence[Scalar], x: float
) -> float:
    """The derivative of the whole chain: every local rate multiplied.

    For the five stages starting at 1.0 this is 2 x 1 x 10 x 0.1 x 0.2 = 0.4,
    and the same chain collapses by hand to ln(2x + 3), whose derivative at
    x = 1 is 2/5. Two routes, one number.

    Approach: one line, calling `product` and `chain_local_rates`.
    """
    return None


def chain_function(stages: Sequence[Scalar]) -> Scalar:
    """Collapse a list of stages into the single function they compose.

    Returns a function, like `compose` does. This is what you feed to
    `central_difference` to check `chain_derivative`.

    Approach: define an inner function that loops the stages over a running
    value, and return it.
    """
    return None


def running_products(rates: Sequence[float]) -> list[float]:
    """The partial products of the local rates, taken from the OUTPUT end.

    Entry i must be the product of rates[i:], so entry 0 is the whole
    derivative and the last entry is just the final local rate. Return the
    list in stage order.

    This is what a backward pass is actually carrying as it walks: after k
    steps from the end, the number in hand is the product of the last k local
    rates.

    For 2, 1, 10, 0.1, 0.2 the answer is about 0.4, 0.2, 0.2, 0.02, 0.2.

    Approach: walk `rates` in reverse with a running total, appending as you
    go, then reverse the list you built.
    """
    return None


# --------------------------------------------------------------------------
# 1.5 -- more than one path
# --------------------------------------------------------------------------


def path_contributions(
    local_rates_per_path: Sequence[Sequence[float]],
) -> list[float]:
    """One number per path: the product of the local rates along that path.

    Approach: one product per path.
    """
    return None


def total_derivative(local_rates_per_path: Sequence[Sequence[float]]) -> float:
    """Multiply along each path, then ADD across paths.

    This is the half of the chain rule that gets dropped. If a variable
    reaches the output by two routes, changing it moves the output twice and
    both movements are real, so they add. For the two paths in the lab the
    contributions are 24 and 12 and the answer is 36 -- not 24, not 12, and
    not 288.

    Approach: sum the contributions.
    """
    return None


# --------------------------------------------------------------------------
# 1.6 -- products that collapse and products that blow up
# --------------------------------------------------------------------------


def repeated_product(factor: float, count: int) -> float:
    """Multiply `factor` by itself `count` times, one multiplication at a time.

    Raise `ValueError` if `count` is negative. A count of zero gives 1.0.

    Write it as a loop rather than as `factor ** count`: the loop is what a
    backward pass through `count` layers actually does.

    Approach: a running total and a `for _ in range(count)` loop.
    """
    return None


def order_of_magnitude(value: float) -> int:
    """floor(log10(|value|)) -- the exponent, ignoring the digits.

    Raise `ValueError` on zero, which has no order of magnitude.

    0.9 to the fiftieth is about 5.15e-3, so its order is -3. Asserting the
    order rather than the digits is the honest way to state a claim about a
    gradient vanishing: the scale is the lesson and the digits are float64
    rounding.

    Approach: `math.floor(math.log10(abs(value)))`, with the guard first.
    """
    return None
