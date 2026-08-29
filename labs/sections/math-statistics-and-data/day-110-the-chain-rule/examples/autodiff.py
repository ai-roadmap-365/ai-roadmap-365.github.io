"""A reverse-mode automatic differentiation engine, in about seventy lines.

This is the core of what every deep-learning framework does. It is not a
simplified illustration of the idea -- it *is* the idea, with the engineering
removed: no tensors, no GPU kernels, no fused operations, no memory planning.
A `Value` holds one number and one gradient, remembers which values it came
from, and knows how to hand its own gradient back to them. `backward()` walks
the graph once in reverse, applying the chain rule at every node.

Two things are worth watching as you read.

**The gradient is accumulated with `+=`, never assigned.** That single choice
is the multivariable chain rule. A value used in two places receives a
contribution from each use, and both are real, so they add. Change either
`+=` below to `=` and the engine will still run, still look sensible, and be
quietly wrong on any graph where something is used twice.

**One backward pass produces every gradient.** Not one pass per parameter --
one pass, total. The forward-mode engine at the bottom of this file does the
opposite, and the two are compared head to head in
`07_vanishing_and_exploding.py`. That asymmetry is the reason training a model
with a hundred million parameters and one loss is affordable at all.
"""

import math
from typing import Callable, Iterable, Sequence


class Value:
    """One number in a computation graph, with a gradient and a history."""

    __slots__ = ("data", "grad", "label", "_backward", "_children", "_op")

    def __init__(
        self,
        data: float,
        children: tuple["Value", ...] = (),
        op: str = "",
        label: str = "",
    ) -> None:
        self.data: float = float(data)
        #: d(final output) / d(this value). Zero until a backward pass fills
        #: it in, and accumulated rather than overwritten.
        self.grad: float = 0.0
        self.label: str = label
        #: Hands this node's gradient back to its children. The identity
        #: function for a leaf, which has no children to hand anything to.
        self._backward: Callable[[], None] = _do_nothing
        self._children: tuple["Value", ...] = children
        self._op: str = op

    # -- the two arithmetic operations -------------------------------------

    def __add__(self, other: "Value | float") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def backward() -> None:
            # Addition passes the gradient through untouched: nudge either
            # input by d and the sum moves by d, so the local rate is 1.
            self.grad += out.grad
            other.grad += out.grad

        out._backward = backward
        return out

    def __mul__(self, other: "Value | float") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def backward() -> None:
            # For a product, each input's local rate is the OTHER input's
            # value. Nudge self by d and the product moves by d * other.
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = backward
        return out

    # -- the one non-linearity ---------------------------------------------

    def tanh(self) -> "Value":
        """The hyperbolic tangent, and the only non-linear operation here.

        One non-linearity is enough to make the network in this lab a genuine
        network rather than a stack of matrix multiplications that collapses
        into one. Its derivative is 1 - tanh squared, which is convenient
        because the forward pass has already computed tanh.
        """
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def backward() -> None:
            self.grad += (1.0 - t * t) * out.grad

        out._backward = backward
        return out

    # -- conveniences built from the two operations above ------------------

    def __neg__(self) -> "Value":
        return self * -1.0

    def __sub__(self, other: "Value | float") -> "Value":
        return self + (-(other if isinstance(other, Value) else Value(other)))

    def __radd__(self, other: "Value | float") -> "Value":
        return self + other

    def __rmul__(self, other: "Value | float") -> "Value":
        return self * other

    def __rsub__(self, other: "Value | float") -> "Value":
        return (-self) + other

    def __repr__(self) -> str:
        name = f"{self.label}=" if self.label else ""
        return f"Value({name}{self.data:.6g}, grad={self.grad:.6g})"

    # -- the backward pass --------------------------------------------------

    def backward(self) -> None:
        """Fill in `.grad` on every value this one was computed from.

        Three steps, and none of them is subtle:

        1. Order the graph so that every node comes after everything it was
           computed from. That is a topological sort, and it matters because a
           node must not hand its gradient onwards until it has received every
           contribution owed to it.
        2. Seed this node's own gradient with 1.0. The derivative of the
           output with respect to itself is 1 -- that is the base case the
           whole chain rule hangs from.
        3. Walk the order backwards, letting each node push its gradient to
           its children by multiplying by the local derivative.
        """
        order = topological_order(self)
        for node in order:
            node.grad = 0.0
        self.grad = 1.0
        for node in reversed(order):
            node._backward()


def _do_nothing() -> None:
    """The backward step of a leaf: it has nobody to pass anything to."""
    return None


def topological_order(root: Value) -> list[Value]:
    """Every value `root` depends on, parents always after their children.

    Iterative rather than recursive, so a chain of ten thousand operations
    does not exhaust the interpreter's stack -- which a deep network's graph
    genuinely would.
    """
    order: list[Value] = []
    visited: set[int] = set()
    # Each stack entry is (node, children_already_expanded).
    stack: list[tuple[Value, bool]] = [(root, False)]
    while stack:
        node, expanded = stack.pop()
        if expanded:
            order.append(node)
            continue
        if id(node) in visited:
            continue
        visited.add(id(node))
        stack.append((node, True))
        for child in node._children:
            if id(child) not in visited:
                stack.append((child, False))
    return order


def graph_size(root: Value) -> int:
    """How many nodes a backward pass will visit."""
    return len(topological_order(root))


# --------------------------------------------------------------------------
# Forward mode, for comparison: the same chain rule, run the other way
# --------------------------------------------------------------------------


class Dual:
    """A number carried alongside its derivative with respect to ONE input.

    Forward mode is the chain rule applied left to right. Every operation
    computes both the value and the rate at which that value moves when the
    chosen input moves. It is simpler than reverse mode -- there is no graph
    and no second pass -- and that simplicity costs it the thing that matters:
    it answers about one input at a time, so a function of n inputs needs n
    separate runs.
    """

    __slots__ = ("value", "dot")

    def __init__(self, value: float, dot: float = 0.0) -> None:
        self.value: float = float(value)
        #: The derivative of this quantity with respect to the seeded input.
        self.dot: float = float(dot)

    def __add__(self, other: "Dual | float") -> "Dual":
        other = other if isinstance(other, Dual) else Dual(other)
        return Dual(self.value + other.value, self.dot + other.dot)

    def __mul__(self, other: "Dual | float") -> "Dual":
        other = other if isinstance(other, Dual) else Dual(other)
        # The product rule, which is the chain rule's travelling companion.
        return Dual(
            self.value * other.value,
            self.dot * other.value + self.value * other.dot,
        )

    def tanh(self) -> "Dual":
        t = math.tanh(self.value)
        return Dual(t, (1.0 - t * t) * self.dot)

    def __neg__(self) -> "Dual":
        return self * -1.0

    def __sub__(self, other: "Dual | float") -> "Dual":
        return self + (-(other if isinstance(other, Dual) else Dual(other)))

    def __radd__(self, other: "Dual | float") -> "Dual":
        return self + other

    def __rmul__(self, other: "Dual | float") -> "Dual":
        return self * other

    def __rsub__(self, other: "Dual | float") -> "Dual":
        return (-self) + other

    def __repr__(self) -> str:
        return f"Dual({self.value:.6g}, dot={self.dot:.6g})"


# --------------------------------------------------------------------------
# The two modes, measured against each other
# --------------------------------------------------------------------------


def reverse_mode_gradient(
    build: Callable[[Sequence[Value]], Value], xs: Sequence[float]
) -> tuple[list[float], int]:
    """Every partial derivative of `build`, and the number of passes used.

    `build` receives one `Value` per input and returns the single output.
    The count returned is the number of forward-and-backward sweeps needed to
    obtain ALL the gradients, and it is 1 no matter how many inputs there are.
    """
    inputs = [Value(x, label=f"x{i}") for i, x in enumerate(xs)]
    out = build(inputs)
    out.backward()
    return [node.grad for node in inputs], 1


def forward_mode_gradient(
    build: Callable[[Sequence[Dual]], Dual], xs: Sequence[float]
) -> tuple[list[float], int]:
    """The same gradients by forward mode, and the number of passes used.

    One pass per input, because each pass can only carry the derivative with
    respect to whichever input was seeded with a 1. The count returned is
    therefore `len(xs)`, and that is the entire argument for reverse mode.
    """
    grads: list[float] = []
    passes = 0
    for seed in range(len(xs)):
        inputs = [
            Dual(x, 1.0 if i == seed else 0.0) for i, x in enumerate(xs)
        ]
        grads.append(build(inputs).dot)
        passes += 1
    return grads, passes


def numeric_gradient(
    f: Callable[[Sequence[float]], float], xs: Sequence[float], h: float
) -> tuple[list[float], int]:
    """The same gradients by central differences, and the passes used.

    Two evaluations per input, so 2n passes -- worse than forward mode and far
    worse than reverse mode, and approximate into the bargain. It is the
    checking tool, not the production tool, and the counts here are why.
    """
    grads: list[float] = []
    passes = 0
    for i in range(len(xs)):
        ahead = list(xs)
        behind = list(xs)
        ahead[i] += h
        behind[i] -= h
        grads.append((f(ahead) - f(behind)) / (2.0 * h))
        passes += 2
    return grads, passes


def parameters_of(root: Value) -> list[Value]:
    """Every leaf in the graph -- the nodes with no children of their own."""
    return [node for node in topological_order(root) if not node._children]


def sum_values(values: Iterable[Value]) -> Value:
    """Add up an iterable of Values, starting from a fresh zero."""
    total = Value(0.0)
    for value in values:
        total = total + value
    return total
