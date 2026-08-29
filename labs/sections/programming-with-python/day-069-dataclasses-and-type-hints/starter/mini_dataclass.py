"""YOUR WORKING FILE — exercise 7: build @dataclass from scratch.

@dataclass is an ordinary decorator. It reads the class's `__annotations__`,
works out the field names and their defaults, builds `__init__`, `__repr__`
and `__eq__` as normal functions, and attaches them to the class. Write that
yourself here, in about forty lines, and the code generation stops being
mysterious.

Reference solution: `examples/mini_dataclass.py`.
"""

from dataclasses import dataclass


# --- EXERCISE 7 ------------------------------------------------------------
# Fill in the three generated methods. Steps:
#
#  a. `names = list(getattr(cls, "__annotations__", {}))` — the field names,
#     in declaration order. Then build `defaults`: for every name that also
#     has a value in the class body (`score: float = 0.0`), record
#     getattr(cls, name). Hint: `name in vars(cls)` tests for that.
#
#  b. __init__(self, *args, **kwargs):
#       - raise TypeError if len(args) > len(names)
#       - `values = dict(zip(names, args))`
#       - for each keyword: TypeError if the key is not a field name, or if
#         it is already filled by a positional argument; otherwise store it
#       - for each name in order: set it from `values`, else from
#         `defaults`, else raise TypeError naming the missing argument
#
#  c. __repr__(self): return f"{cls.__name__}(...)" where ... is the fields
#     joined with ", " as `name=value!r` — use an f-string with `!r`.
#
#  d. __eq__(self, other): return NotImplemented unless
#     `other.__class__ is cls`; otherwise compare the two lists of field
#     values.
#
#  e. Attach all three to `cls`, set `cls.__hash__ = None` (the real
#     @dataclass does the same when it generates __eq__ without frozen=True),
#     and return `cls`.
def mini_dataclass(cls):
    """Attach a generated __init__, __repr__ and __eq__ to `cls`."""

    def unfinished__init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Exercise 7: read cls.__annotations__ and generate __init__, "
            "__repr__ and __eq__."
        )

    # Replace this stub with the real generation described above. It is here
    # so the module still imports while the exercise is unfinished.
    cls.__init__ = unfinished__init__
    return cls


@mini_dataclass
class MiniRecord:
    """Three fields, built by your decorator."""

    prompt: str
    expected: str
    score: float = 0.0


@dataclass
class RealRecord:
    """The same three fields, built by the real @dataclass — the control."""

    prompt: str
    expected: str
    score: float = 0.0
