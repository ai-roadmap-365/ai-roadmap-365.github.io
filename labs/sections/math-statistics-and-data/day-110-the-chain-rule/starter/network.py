"""Exercise 4 -- backpropagate the tiny network by hand, then by your engine.

The forward pass and the graph builder are written for you, because they are
not the exercise. The exercise is the backward pass: writing out every local
derivative and multiplying along every path, with your own arithmetic, and
then watching your engine from exercise 2 produce the identical numbers.

The network is two inputs, two tanh hidden units, one linear output, a
squared-error loss, and nine parameters. Every quantity in both passes is
exact in float64, so you can check the whole thing with a pen. Read
`dataset.py` for the values and for why the bias of unit B is half the
natural logarithm of 3.
"""

import math
from typing import Sequence

import dataset as D
from autodiff import Value


def forward(x1: float, x2: float, params: Sequence[float]) -> dict[str, float]:
    """Run the network in plain floats. Written for you."""
    wA1, wA2, bA, wB1, wB2, bB, vA, vB, c = params
    a_pre = wA1 * x1 + wA2 * x2 + bA
    a = math.tanh(a_pre)
    b_pre = wB1 * x1 + wB2 * x2 + bB
    b = math.tanh(b_pre)
    out = vA * a + vB * b + c
    loss = (out - D.NET_TARGET) * (out - D.NET_TARGET)
    return {
        "a_pre": a_pre,
        "a": a,
        "b_pre": b_pre,
        "b": b,
        "out": out,
        "loss": loss,
    }


def loss_only(x1: float, x2: float, params: Sequence[float]) -> float:
    """Just the loss, for feeding to a central difference. Written for you."""
    return forward(x1, x2, params)["loss"]


def default_parameter_values() -> list[float]:
    """The nine parameters, in the documented order. Written for you."""
    return [
        D.NET_WA1,
        D.NET_WA2,
        D.NET_BA,
        D.NET_WB1,
        D.NET_WB2,
        D.NET_BB,
        D.NET_VA,
        D.NET_VB,
        D.NET_C,
    ]


def build_graph(
    x1: Value, x2: Value, params: Sequence[Value]
) -> dict[str, Value]:
    """The same network built out of your `Value` class. Written for you.

    This will not work until exercise 2 does, which is deliberate: the graph
    is only as good as the operations it is built from.
    """
    wA1, wA2, bA, wB1, wB2, bB, vA, vB, c = params
    a_pre = wA1 * x1 + wA2 * x2 + bA
    a = a_pre.tanh()
    b_pre = wB1 * x1 + wB2 * x2 + bB
    b = b_pre.tanh()
    out = vA * a + vB * b + c
    diff = out - D.NET_TARGET
    loss = diff * diff
    return {
        "x1": x1,
        "x2": x2,
        "wA1": wA1,
        "wA2": wA2,
        "bA": bA,
        "wB1": wB1,
        "wB2": wB2,
        "bB": bB,
        "vA": vA,
        "vB": vB,
        "c": c,
        "a_pre": a_pre,
        "a": a,
        "b_pre": b_pre,
        "b": b,
        "out": out,
        "loss": loss,
    }


# --------------------------------------------------------------------------
# 4a -- the backward pass, by hand
# --------------------------------------------------------------------------


def hand_gradients() -> dict[str, float]:
    """Return every gradient in the network, computed by your own arithmetic.

    The keys must be exactly these sixteen:

        out, c, vA, vB, a, b, a_pre, b_pre,
        wA1, wA2, bA, wB1, wB2, bB, x1, x2

    Work from the end backwards. The seed is d(loss)/d(loss) = 1, and:

        loss = (out - target) squared    ->  d loss/d out = 2 x (out - target)
        out  = vA*a + vB*b + c           ->  local rates 1, a, b, vA, vB
        a    = tanh(a_pre)               ->  local rate 1 - a squared
        a_pre = wA1*x1 + wA2*x2 + bA     ->  local rates x1, x2, 1, wA1, wA2

    Two of the sixteen are worth thinking about before you write them.

    `vA` multiplies an activation of exactly 0, so ask yourself what nudging
    vA does to the output before you reach for a formula.

    `x1` and `x2` each reach the loss through BOTH hidden units. Each of
    those two gradients is therefore a SUM of two products, not a single
    product. This is the one place in the lab where getting it wrong still
    produces a completely reasonable-looking number, and the test that checks
    it compares against a central difference, which has no opinion about
    which path you meant.

    Approach: read the forward values out of `forward(...)` or straight from
    `dataset.py`, then write one line per gradient in the order above. Do not
    call your engine here -- the whole point is that the two agree.
    """
    return None


# --------------------------------------------------------------------------
# 4b -- the same thing from the engine, in one backward pass
# --------------------------------------------------------------------------


def engine_gradients() -> dict[str, float]:
    """Return every gradient in the network, from ONE backward pass.

    Build `Value` nodes for x1, x2 and the nine parameters, pass them to
    `build_graph`, call `.backward()` on the loss node, and read `.grad` off
    every node in the returned dictionary.

    If exercise 2 is correct, this will match `hand_gradients` bit for bit --
    not approximately, exactly -- because it performs the same
    multiplications in the same order on the same exact values.

    Approach: four lines, ending in a dictionary comprehension over the
    dictionary that `build_graph` returns.
    """
    return None


# --------------------------------------------------------------------------
# 4c -- the numerical cross-check
# --------------------------------------------------------------------------


def numeric_parameter_gradients(h: float) -> dict[str, float]:
    """Every parameter gradient by central difference, keyed by name.

    Nudge one parameter at a time by +h and -h, holding the rest still, and
    divide the change in the loss by 2h. The names are in
    `dataset.NET_PARAMETERS`, in the same order as
    `default_parameter_values()`.

    These will NOT match the other two exactly, and they should not. A
    central difference has its own error, which is why the test suite
    compares it with a tolerance a million times looser than the one it uses
    between your hand computation and your engine.

    Approach: a loop over `enumerate(D.NET_PARAMETERS)`, two copies of the
    parameter list per step, and `loss_only` for the evaluations.
    """
    return None
