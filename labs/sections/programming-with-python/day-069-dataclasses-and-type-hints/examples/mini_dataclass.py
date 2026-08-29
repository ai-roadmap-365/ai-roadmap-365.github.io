"""Reference solution: a decorator that does what @dataclass does.

`@dataclass` is not magic. It is a decorator that reads the class's
`__annotations__`, works out the field names and their defaults, builds
`__init__`, `__repr__` and `__eq__` as ordinary functions, and attaches them
to the class. This file does the same thing in about forty lines so you can
see the whole trick.

The real `@dataclass` builds its methods by generating source text and
running `exec` on it (which is how it gets a genuine parameter list, and why
`help()` shows a real signature). This version builds closures instead:
simpler to read, and behaviourally the same for the cases the lab checks.
"""

from dataclasses import dataclass


def mini_dataclass(cls):
    """Attach a generated __init__, __repr__ and __eq__ to `cls`.

    Fields are the names annotated in the class body, in declaration order.
    A name that also has a value in the class body (`score: float = 0.0`)
    becomes a default; everything else is required.
    """
    names = list(getattr(cls, "__annotations__", {}))
    defaults = {name: getattr(cls, name) for name in names if name in vars(cls)}

    def __init__(self, *args, **kwargs):
        if len(args) > len(names):
            raise TypeError(
                f"{cls.__name__}() takes at most {len(names)} arguments"
            )
        values = dict(zip(names, args))
        for key, value in kwargs.items():
            if key not in names:
                raise TypeError(
                    f"{cls.__name__}() got an unexpected keyword argument {key!r}"
                )
            if key in values:
                raise TypeError(
                    f"{cls.__name__}() got multiple values for argument {key!r}"
                )
            values[key] = value
        for name in names:
            if name in values:
                setattr(self, name, values[name])
            elif name in defaults:
                setattr(self, name, defaults[name])
            else:
                raise TypeError(
                    f"{cls.__name__}() missing required argument {name!r}"
                )

    def __repr__(self):
        inner = ", ".join(f"{name}={getattr(self, name)!r}" for name in names)
        return f"{cls.__name__}({inner})"

    def __eq__(self, other):
        if other.__class__ is not cls:
            return NotImplemented
        return [getattr(self, name) for name in names] == [
            getattr(other, name) for name in names
        ]

    cls.__init__ = __init__
    cls.__repr__ = __repr__
    cls.__eq__ = __eq__
    cls.__hash__ = None  # matches @dataclass: eq without frozen drops __hash__
    return cls


@mini_dataclass
class MiniRecord:
    """Three fields, built by the mini decorator."""

    prompt: str
    expected: str
    score: float = 0.0


@dataclass
class RealRecord:
    """The same three fields, built by the real @dataclass — the control."""

    prompt: str
    expected: str
    score: float = 0.0
