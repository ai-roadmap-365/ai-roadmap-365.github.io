"""Exercise 2 -- build the reverse-mode autodiff engine.

This is the most valuable thing in the calculus arc. When it works you will
have written the core of what every deep-learning framework does, and checked
it against a numerical derivative that knows nothing about your graph.

Work in this order, checking with `pytest starter -q` after each step:

    2a  __add__          the value, and both local rates of 1
    2b  __mul__          the value, and each local rate being the OTHER input
    2c  tanh             the value, and the local rate 1 - tanh squared
    2d  topological_order   children always before parents
    2e  backward         seed 1.0, then walk the order in reverse
    2f  Dual             forward mode, for the cost comparison

The single most important line in the whole file is the one that accumulates
a gradient with `+=` rather than assigning it with `=`. That one character is
the multivariable chain rule: a value used in two places receives a
contribution from each use, and both are real, so they add. Get it wrong and
the engine will still run, still look sensible, and be quietly wrong on every
graph where anything is used twice.
"""

import math
from typing import Callable, Sequence


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
        self.grad: float = 0.0
        self.label: str = label
        self._backward: Callable[[], None] = _do_nothing
        self._children: tuple["Value", ...] = children
        self._op: str = op

    # -- 2a ----------------------------------------------------------------

    def __add__(self, other: "Value | float") -> "Value":
        """Return a new Value holding self.data + other.data.

        The new Value's children are (self, other) and its op is "+".

        Then give it a `_backward` function that adds `out.grad` to BOTH
        children's gradients -- addition passes the gradient through
        untouched, because nudging either input by d moves the sum by d.

        Approach:

            other = other if isinstance(other, Value) else Value(other)
            out = Value(self.data + other.data, (self, other), "+")
            def backward():
                self.grad += out.grad
                other.grad += out.grad
            out._backward = backward
            return out

        That approach block is the answer, written out, because the shape of
        this method is the shape of all three and it is worth having one to
        copy from. The next two are yours.
        """
        return None

    # -- 2b ----------------------------------------------------------------

    def __mul__(self, other: "Value | float") -> "Value":
        """Return a new Value holding self.data * other.data, op "*".

        For a product, each input's local rate is the OTHER input's value:
        nudge self by d and the product moves by d x other.data. So the
        backward step adds `other.data * out.grad` to self.grad, and
        `self.data * out.grad` to other.grad.

        Use `+=` for both. Check it afterwards with `x * x`, where x is used
        twice: if the answer for x = 3 is 6.0 you have it right, and if it is
        3.0 you assigned where you should have accumulated.
        """
        return None

    # -- 2c ----------------------------------------------------------------

    def tanh(self) -> "Value":
        """Return a new Value holding tanh(self.data), op "tanh".

        The derivative of tanh is 1 - tanh squared. Compute the tanh once,
        before building the output, and reuse it in the backward step rather
        than recomputing it -- that reuse is exactly what a real framework
        does, and it is why a backward pass needs the forward pass's values
        kept in memory.

        Check: tanh at 0 has slope exactly 1, and at half the natural log of
        3 it has value exactly 0.5 and slope exactly 0.75.
        """
        return None

    # -- conveniences, already written for you -----------------------------

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

    # -- 2e ----------------------------------------------------------------

    def backward(self) -> None:
        """Fill in `.grad` on every value this one was computed from.

        Four steps:

        1. Get the topological order of the graph (exercise 2d).
        2. Zero every gradient, so calling backward twice gives the same
           answer as calling it once.
        3. Set this node's own grad to 1.0 -- the derivative of the output
           with respect to itself, which is the base case everything else
           hangs from.
        4. Walk the order BACKWARDS, calling each node's `_backward()`.

        Step 4 must be in reverse topological order, not any order that
        happens to work on a straight chain. A node must have received every
        contribution owed to it before it passes any of them on, and on a
        branching graph an arbitrary order will silently lose one.

        This function returns None on purpose -- it fills in gradients as a
        side effect. The test suite decides you have attempted it by checking
        whether a gradient actually changed.
        """
        return None


def _do_nothing() -> None:
    """The backward step of a leaf: it has nobody to pass anything to."""
    return None


# -- 2d --------------------------------------------------------------------


def topological_order(root: Value) -> list[Value]:
    """Every value `root` depends on, parents always AFTER their children.

    Write it iteratively rather than recursively. A chain of ten thousand
    operations is an ordinary size for a computation graph and would exhaust
    the interpreter's stack; one of the reference tests builds exactly that.

    A node reached twice must appear exactly once in the result.

    Approach: a stack of (node, already_expanded) pairs. Pop one; if it is
    already expanded, append it to the output. Otherwise mark it visited,
    push it back as expanded, and push its unvisited children. Track visited
    nodes by `id(node)`, because Value has no meaningful equality.
    """
    return None


def graph_size(root: Value) -> int:
    """How many nodes a backward pass will visit.

    Approach: one line, once `topological_order` works.
    """
    return None


# -- 2f --------------------------------------------------------------------


class Dual:
    """A number carried alongside its derivative with respect to ONE input.

    Forward mode: the same chain rule, applied left to right. Each operation
    computes the value AND the rate at which that value moves when the
    seeded input moves. There is no graph and no second pass, and the price
    is that one run answers about one input only.
    """

    __slots__ = ("value", "dot")

    def __init__(self, value: float, dot: float = 0.0) -> None:
        self.value: float = float(value)
        self.dot: float = float(dot)

    def __add__(self, other: "Dual | float") -> "Dual":
        """Add both parts: values add, and derivatives add.

        Remember to accept a plain float on the right, as `Value` does.
        """
        return None

    def __mul__(self, other: "Dual | float") -> "Dual":
        """The product rule.

        The value is self.value x other.value. The derivative is

            self.dot x other.value  +  self.value x other.dot

        which is the product rule, and which is the chain rule's constant
        travelling companion.
        """
        return None

    def tanh(self) -> "Dual":
        """tanh of the value, with the derivative scaled by 1 - tanh squared."""
        return None

    # -- conveniences, already written for you -----------------------------

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
# Exercise 3 -- the two modes, and their cost
# --------------------------------------------------------------------------


def reverse_mode_gradient(
    build: Callable[[Sequence[Value]], Value], xs: Sequence[float]
) -> tuple[list[float], int]:
    """Every partial derivative of `build`, and the number of passes used.

    `build` receives one `Value` per entry of `xs` and returns one output
    Value. Build the inputs, call `build`, call `.backward()` on the output,
    and return the list of input gradients together with the pass count.

    The pass count is 1, always, no matter how many inputs there are. That
    is the entire point of reverse mode, and the test suite checks it.
    """
    return None


def forward_mode_gradient(
    build: Callable[[Sequence[Dual]], Dual], xs: Sequence[float]
) -> tuple[list[float], int]:
    """The same gradients by forward mode, and the number of passes used.

    Run `build` once per input. On run number k, seed input k with a dot of
    1.0 and every other input with 0.0; the output's `.dot` is then the
    partial derivative with respect to input k.

    The pass count is `len(xs)`. Comparing that against the 1 above, on a
    model with a hundred million parameters, is the whole argument.
    """
    return None


def numeric_gradient(
    f: Callable[[Sequence[float]], float], xs: Sequence[float], h: float
) -> tuple[list[float], int]:
    """The same gradients by central differences, and the passes used.

    Two evaluations per input, so the count is 2 x len(xs) -- worse than
    forward mode and far worse than reverse mode, and approximate as well.
    This is the checking tool, not the production tool.

    `f` takes a whole list of coordinates, not one at a time.
    """
    return None
