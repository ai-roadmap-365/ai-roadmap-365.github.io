"""The tiny two-layer network the lab backpropagates by hand.

Two inputs, two hidden units with a tanh non-linearity, one linear output, and
a squared-error loss. Nine parameters. That is small enough to differentiate
on paper and large enough to contain every structural feature of a real
network -- including the one that matters most today: each input reaches the
loss through **both** hidden units, so its gradient is a sum over two paths
rather than a single product.

The numbers were chosen so that every quantity in both passes is exact in
float64. Hidden unit A sits at a pre-activation of exactly 0, where tanh is 0
and its slope is 1. Hidden unit B sits at exactly half the natural logarithm
of 3, where tanh is exactly 0.5 and its slope is exactly 0.75. Those two
facts are asserted by the test suite rather than assumed, and the choice is a
convenience for the reader rather than anything the chain rule depends on.
"""

from typing import Sequence

import dataset as D
from autodiff import Dual, Value


def forward(
    x1: float, x2: float, params: Sequence[float]
) -> dict[str, float]:
    """Run the network in plain floats and return every intermediate value.

    `params` is in the order given by `dataset.NET_PARAMETERS`:
    wA1, wA2, bA, wB1, wB2, bB, vA, vB, c.
    """
    import math

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
    """Just the loss, for feeding to a central difference."""
    return forward(x1, x2, params)["loss"]


def build_graph(
    x1: Value, x2: Value, params: Sequence[Value]
) -> dict[str, Value]:
    """Build the same network out of `Value` nodes and return them all.

    The returned dictionary is keyed the same way as `dataset.NET_GRADIENTS`,
    so a test can walk the two side by side.
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


def default_parameter_values() -> list[float]:
    """The nine parameters from `dataset.py`, in the documented order."""
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


def engine_gradients() -> dict[str, float]:
    """Every gradient in the network, from one backward pass of the engine."""
    x1 = Value(D.NET_X1, label="x1")
    x2 = Value(D.NET_X2, label="x2")
    params = [
        Value(v, label=name)
        for name, v in zip(D.NET_PARAMETERS, default_parameter_values())
    ]
    nodes = build_graph(x1, x2, params)
    nodes["loss"].backward()
    return {name: node.grad for name, node in nodes.items()}


def hand_gradients() -> dict[str, float]:
    """The same gradients, written out as the arithmetic of the backward pass.

    This function deliberately repeats by hand what `engine_gradients` gets
    from the graph walk. Every line is one application of the chain rule, and
    the two lines marked SUM are where two paths meet and are added.
    """
    x1, x2 = D.NET_X1, D.NET_X2
    a, b = D.NET_A, D.NET_B
    out = D.NET_OUT

    # The seed: d(loss)/d(loss) = 1, and loss = (out - target) squared.
    d_out = 2.0 * (out - D.NET_TARGET)

    # Output layer: out = vA*a + vB*b + c.
    d_c = d_out * 1.0
    d_vA = d_out * a
    d_vB = d_out * b
    d_a = d_out * D.NET_VA
    d_b = d_out * D.NET_VB

    # Through the non-linearity: a = tanh(a_pre), so da/da_pre = 1 - a^2.
    d_a_pre = d_a * (1.0 - a * a)
    d_b_pre = d_b * (1.0 - b * b)

    # First layer: a_pre = wA1*x1 + wA2*x2 + bA.
    d_wA1 = d_a_pre * x1
    d_wA2 = d_a_pre * x2
    d_bA = d_a_pre * 1.0
    d_wB1 = d_b_pre * x1
    d_wB2 = d_b_pre * x2
    d_bB = d_b_pre * 1.0

    # The inputs reach the loss through BOTH hidden units. SUM the paths.
    d_x1 = d_a_pre * D.NET_WA1 + d_b_pre * D.NET_WB1  # SUM over two paths
    d_x2 = d_a_pre * D.NET_WA2 + d_b_pre * D.NET_WB2  # SUM over two paths

    return {
        "out": d_out,
        "c": d_c,
        "vA": d_vA,
        "vB": d_vB,
        "a": d_a,
        "b": d_b,
        "a_pre": d_a_pre,
        "b_pre": d_b_pre,
        "wA1": d_wA1,
        "wA2": d_wA2,
        "bA": d_bA,
        "wB1": d_wB1,
        "wB2": d_wB2,
        "bB": d_bB,
        "x1": d_x1,
        "x2": d_x2,
    }


def numeric_parameter_gradients(h: float) -> dict[str, float]:
    """Every parameter gradient by central difference, for cross-checking."""
    base = default_parameter_values()
    grads: dict[str, float] = {}
    for i, name in enumerate(D.NET_PARAMETERS):
        ahead = list(base)
        behind = list(base)
        ahead[i] += h
        behind[i] -= h
        grads[name] = (
            loss_only(D.NET_X1, D.NET_X2, ahead)
            - loss_only(D.NET_X1, D.NET_X2, behind)
        ) / (2.0 * h)
    return grads


def numeric_input_gradients(h: float) -> dict[str, float]:
    """The two input gradients by central difference.

    These are the two that are sums over paths, so they are the two worth
    checking hardest: a product-only chain rule gets them visibly wrong.
    """
    params = default_parameter_values()
    grads: dict[str, float] = {}
    for name, i in (("x1", 0), ("x2", 1)):
        point = [D.NET_X1, D.NET_X2]
        ahead = list(point)
        behind = list(point)
        ahead[i] += h
        behind[i] -= h
        grads[name] = (
            loss_only(ahead[0], ahead[1], params)
            - loss_only(behind[0], behind[1], params)
        ) / (2.0 * h)
    return grads


def forward_mode_parameter_gradients() -> tuple[dict[str, float], int]:
    """Every parameter gradient by forward mode, and the passes it needed.

    One complete run of the network per parameter. With nine parameters that
    is nine runs to reverse mode's one, and the ratio is the whole reason
    training uses reverse mode.
    """
    base = default_parameter_values()
    grads: dict[str, float] = {}
    passes = 0
    for seed, name in enumerate(D.NET_PARAMETERS):
        x1 = Dual(D.NET_X1, 0.0)
        x2 = Dual(D.NET_X2, 0.0)
        params = [
            Dual(v, 1.0 if i == seed else 0.0) for i, v in enumerate(base)
        ]
        wA1, wA2, bA, wB1, wB2, bB, vA, vB, c = params
        a = (wA1 * x1 + wA2 * x2 + bA).tanh()
        b = (wB1 * x1 + wB2 * x2 + bB).tanh()
        out = vA * a + vB * b + c
        diff = out - D.NET_TARGET
        grads[name] = (diff * diff).dot
        passes += 1
    return grads, passes
