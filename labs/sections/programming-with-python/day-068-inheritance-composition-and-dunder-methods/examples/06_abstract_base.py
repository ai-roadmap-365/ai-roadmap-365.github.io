"""Step 6: an abstract base class, and the duck typing that often replaces it.

An abstract base class cannot be instantiated, and it names the methods every
subclass must implement. Forget one and Python refuses to build the object at
the moment you asked for it, naming the class and the missing method — far
kinder than a mysterious failure hours into a run.

Note the shape of `Station.announce`: a CONCRETE method that calls an
ABSTRACT one. That is the template-method pattern, and it is exactly how
PyTorch's nn.Module works — the framework calls the `forward` you wrote.

Run it:  python3 examples/06_abstract_base.py
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sized


class Station(ABC):
    """Every station has a name and must know how to prepare a dish."""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def prepare(self, dish):
        """Return a string describing how this station prepares the dish."""

    def announce(self, dish):  # concrete, shared, calls the abstract method
        return f"{self.name}: {self.prepare(dish)}"


class GrillStation(Station):
    def prepare(self, dish):
        return f"grilling {dish} over charcoal"


class PastryStation(Station):
    """Deliberately incomplete: `prepare` was never implemented."""


def main():
    print(GrillStation("Grill").announce("mackerel"))

    try:
        PastryStation("Pastry")
    except TypeError as err:
        print(f"TypeError: {err}")

    print("    ^ refused at CONSTRUCTION, naming the class and the method.")
    print(f"abstract methods still outstanding: "
          f"{sorted(PastryStation.__abstractmethods__)}")

    print()
    print("-- but Python did not need the ABC to make this work --")

    class Ticket:
        """Inherits from nothing but object, yet satisfies a protocol."""

        def __init__(self, items):
            self.items = items

        def __iter__(self):
            return iter(self.items)

    ticket = Ticket(["mackerel", "gyoza"])
    print(f"isinstance(t, Iterable): {isinstance(ticket, Iterable)}")
    print(f"isinstance(t, Sized):    {isinstance(ticket, Sized)}")
    print(f'hasattr(t, "__iter__"):  {hasattr(ticket, "__iter__")}')
    try:
        len(ticket)
    except TypeError as err:
        print(f"len(t) -> TypeError: {err}")
    print("    ^ Iterable is True because Ticket defines __iter__ — the check")
    print("      is for the METHOD, not for the family tree.")


if __name__ == "__main__":
    main()
