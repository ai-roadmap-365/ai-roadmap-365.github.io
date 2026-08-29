"""The chain rule, written out in code: local rates, products, and paths.

Nothing in this module knows anything about neural networks. It knows that
when one quantity depends on another which depends on another, the rates
multiply -- and that when a quantity reaches the output by more than one
route, the routes are added.

Every function here is checked against a central difference in
`test_reference.py`, which is the whole point of the day: the chain rule is
not a rule to be believed, it is a rule that can be measured.
"""

import math
from typing import Callable, Iterable, Sequence

Scalar = Callable[[float], float]


# --------------------------------------------------------------------------
# The measuring instrument, carried over from Day 108
# --------------------------------------------------------------------------


def central_difference(f: Scalar, x: float, h: float) -> float:
    """Estimate f'(x) by straddling x: (f(x+h) - f(x-h)) / (2h).

    This is the checking tool for the whole lab. It knows nothing about the
    chain rule -- it just moves x a little and watches the output move -- and
    that independence is what makes it a valid check.
    """
    if h <= 0.0:
        raise ValueError("h must be positive")
    return (f(x + h) - f(x - h)) / (2.0 * h)


def partial_difference(
    f: Callable[..., float], point: Sequence[float], index: int, h: float
) -> float:
    """Estimate one partial derivative of a multi-input function.

    Nudge coordinate `index` and hold every other coordinate still. This is
    Day 109's tool, and it is what the multivariable chain rule is checked
    against here.
    """
    if h <= 0.0:
        raise ValueError("h must be positive")
    ahead = list(point)
    behind = list(point)
    ahead[index] += h
    behind[index] -= h
    return (f(*ahead) - f(*behind)) / (2.0 * h)


# --------------------------------------------------------------------------
# Rates multiply: the idea with no calculus in it at all
# --------------------------------------------------------------------------


def product(factors: Iterable[float]) -> float:
    """Multiply an iterable of numbers together.

    An empty product is 1.0, which is the identity for multiplication and is
    also the right answer to "how much does x change per unit of x".
    """
    total = 1.0
    for factor in factors:
        total *= factor
    return total


def gear_ratio(ratios: Iterable[float]) -> float:
    """The overall ratio of a gear train: every stage ratio multiplied.

    If the first gear turns twice per turn of the second, and the second turns
    three times per turn of the third, the first turns six times per turn of
    the third. That sentence is the chain rule with the notation removed.
    """
    return product(ratios)


# --------------------------------------------------------------------------
# Composition, and the one-variable chain rule
# --------------------------------------------------------------------------


def compose(outer: Scalar, inner: Scalar) -> Scalar:
    """Return the function x -> outer(inner(x)).

    Read the parentheses from the inside out: `inner` runs first on x, and
    `outer` runs on whatever came back.
    """

    def composed(x: float) -> float:
        return outer(inner(x))

    return composed


def chain_rule(
    d_outer: Scalar, inner: Scalar, d_inner: Scalar, x: float
) -> float:
    """The chain rule for one variable, in one line.

    dy/dx = dy/du * du/dx, where u = inner(x). The outer derivative is
    evaluated **at the inner value**, not at x -- which is the single most
    common way to get this wrong, and the reason the argument is written out
    here instead of being tucked into a lambda.
    """
    u = inner(x)
    return d_outer(u) * d_inner(x)


# --------------------------------------------------------------------------
# Chains of any length
# --------------------------------------------------------------------------


def chain_values(stages: Sequence[Scalar], x: float) -> list[float]:
    """The forward pass: every intermediate value, starting with x itself.

    For n stages this returns n + 1 numbers: the input, then the output of
    each stage in turn. Keeping the input in the list means value[i] is
    always the input to stage i, which makes the backward pass easy to read.
    """
    values = [x]
    current = x
    for stage in stages:
        current = stage(current)
        values.append(current)
    return values


def chain_local_rates(
    stages: Sequence[Scalar], rates: Sequence[Scalar], x: float
) -> list[float]:
    """The local derivative of every stage, each evaluated at its own input.

    This is the step people skip. Stage i's derivative is evaluated at the
    value that *arrives* at stage i, which is the output of stage i-1 -- not
    at x, and not at the final answer.
    """
    if len(stages) != len(rates):
        raise ValueError("every stage needs exactly one derivative")
    values = chain_values(stages, x)
    return [rate(values[i]) for i, rate in enumerate(rates)]


def chain_derivative(
    stages: Sequence[Scalar], rates: Sequence[Scalar], x: float
) -> float:
    """The derivative of the whole chain: every local rate multiplied.

    This is the chain rule for a composition of any depth. Two functions or
    two hundred, the shape does not change -- which is exactly why a network
    with a hundred layers is trainable at all.
    """
    return product(chain_local_rates(stages, rates, x))


def chain_function(stages: Sequence[Scalar]) -> Scalar:
    """Collapse a list of stages into the single function they compose."""

    def composed(x: float) -> float:
        current = x
        for stage in stages:
            current = stage(current)
        return current

    return composed


def running_products(rates: Sequence[float]) -> list[float]:
    """The partial products of the local rates, taken from the output end.

    This is what a backward pass actually computes: after visiting k stages
    from the end, the number it is carrying is the product of the last k
    local rates. The list is returned in stage order, so entry i is the
    gradient of the output with respect to the value arriving at stage i.
    """
    out: list[float] = []
    carried = 1.0
    for rate in reversed(rates):
        carried *= rate
        out.append(carried)
    out.reverse()
    return out


# --------------------------------------------------------------------------
# More than one path: the part where contributions ADD
# --------------------------------------------------------------------------


def path_contributions(local_rates_per_path: Sequence[Sequence[float]]) -> list[float]:
    """One number per path: the product of the local rates along that path."""
    return [product(path) for path in local_rates_per_path]


def total_derivative(local_rates_per_path: Sequence[Sequence[float]]) -> float:
    """Multiply along each path, then ADD across paths.

    The addition is the half that gets dropped. If a variable influences the
    output through two routes, changing it moves the output twice, and both
    movements happen. There is no rule of nature that makes one of them the
    real one.
    """
    return sum(path_contributions(local_rates_per_path))


def wrong_single_path_derivative(
    local_rates_per_path: Sequence[Sequence[float]], path_index: int = 0
) -> float:
    """The mistake, implemented deliberately so a test can catch it.

    This takes one path's product and stops. It is here to be compared
    against `total_derivative` and against a central difference, so that the
    failure is a measurement rather than a warning in a comment.
    """
    return product(local_rates_per_path[path_index])


# --------------------------------------------------------------------------
# Products that collapse and products that blow up
# --------------------------------------------------------------------------


def repeated_product(factor: float, count: int) -> float:
    """Multiply `factor` by itself `count` times, one multiplication at a time.

    Written as a loop rather than as `factor ** count` because the loop is
    what a backward pass through `count` layers actually does, and because the
    intermediate values are the interesting part.
    """
    if count < 0:
        raise ValueError("count must not be negative")
    total = 1.0
    for _ in range(count):
        total *= factor
    return total


def product_trace(factor: float, count: int) -> list[float]:
    """Every running value of `repeated_product`, for plotting or printing."""
    trace: list[float] = []
    total = 1.0
    for _ in range(count):
        total *= factor
        trace.append(total)
    return trace


def order_of_magnitude(value: float) -> int:
    """floor(log10(|value|)) -- the exponent, ignoring the digits.

    Vanishing and exploding gradients are a statement about scale, so this is
    what the tests assert. Claiming an exact value for 0.9 to the fiftieth
    power would be asserting float64 rounding, which is not the lesson.
    """
    if value == 0.0:
        raise ValueError("zero has no order of magnitude")
    return math.floor(math.log10(abs(value)))
