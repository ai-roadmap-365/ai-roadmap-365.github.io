"""Step 3: the same domain modelled twice — inheritance, then composition.

Both halves of this file produce the SAME behaviour for an Oven and a
Toaster. Only the structure differs:

  inheritance   Oven IS-A HeatingAppliance IS-A Appliance.
                Behaviour arrives implicitly, found by walking the MRO.
                Fixed at class-definition time.

  composition   Oven HAS-A HeatingElement and HAS-A Timer.
                Behaviour is forwarded explicitly (delegation).
                Swappable at runtime.

After running this, write your comparison into starter/comparison.md.

Run it:  python3 examples/03_composition.py
"""


# ---------------------------------------------------------------- inheritance
class Appliance:
    def __init__(self, name, watts):
        self.name = name
        self.watts = watts

    def describe(self):
        return f"{self.name} ({self.watts}W)"


class HeatingAppliance(Appliance):
    def __init__(self, name, watts, max_celsius):
        super().__init__(name, watts)
        self.max_celsius = max_celsius

    def heat(self, celsius):
        if celsius > self.max_celsius:
            raise ValueError(f"{self.name} cannot exceed {self.max_celsius}C")
        return f"heating to {celsius}C at {self.watts}W"


class InheritedOven(HeatingAppliance):
    def __init__(self, name, watts, max_celsius, capacity_litres):
        super().__init__(name, watts, max_celsius)
        self.capacity_litres = capacity_litres

    def describe(self):  # extend, do not replace
        return f"{super().describe()}, {self.capacity_litres}L"


class InheritedToaster(HeatingAppliance):
    def __init__(self, name, watts, max_celsius, slots):
        super().__init__(name, watts, max_celsius)
        self.slots = slots


# ---------------------------------------------------------------- composition
class HeatingElement:
    """A collaborator. Knows how to heat, and nothing else."""

    def __init__(self, watts):
        self.watts = watts

    def heat(self, celsius):
        return f"heating to {celsius}C at {self.watts}W"


class Timer:
    """A second collaborator, entirely independent of the first."""

    def __init__(self):
        self.minutes = 0

    def set(self, minutes):
        self.minutes = minutes
        return f"timer set to {minutes} min"


class FanAssistedElement(HeatingElement):
    """A drop-in replacement, to show the swap is real."""

    def heat(self, celsius):
        return f"fan-assisted to {celsius}C at {self.watts}W"


class ComposedOven:
    def __init__(self, name, watts):
        self.name = name
        self.element = HeatingElement(watts)  # has-a
        self.timer = Timer()                  # has-a

    def bake(self, celsius, minutes):         # delegation, written by hand
        return f"{self.name}: {self.element.heat(celsius)}; {self.timer.set(minutes)}"


class ComposedToaster:
    def __init__(self, name, watts):
        self.name = name
        self.element = HeatingElement(watts)  # has-a, no shared ancestor

    def toast(self, celsius):
        return f"{self.name}: {self.element.heat(celsius)}"


def main():
    print("-- inheritance: behaviour arrives implicitly through the MRO --")
    oven = InheritedOven("Deck oven", 3200, 260, 60)
    print(oven.describe())
    print(oven.heat(220), "   <- defined on HeatingAppliance, not on Oven")
    print(f"MRO: {' -> '.join(c.__name__ for c in InheritedOven.__mro__)}")
    print(f"Toaster shares the whole chain: "
          f"{' -> '.join(c.__name__ for c in InheritedToaster.__mro__)}")

    print()
    print("-- composition: behaviour is forwarded explicitly --")
    print(ComposedOven("Deck oven", 3200).bake(220, 35))
    print(ComposedToaster("Two-slice", 900).toast(260))
    print(f"ComposedOven inherits from: "
          f"{[c.__name__ for c in ComposedOven.__mro__]}  <- nothing but object")

    print()
    print("-- the practical difference: swap a collaborator at runtime --")
    swappable = ComposedOven("Deck oven", 3200)
    swappable.element = FanAssistedElement(3200)   # one assignment
    print(swappable.bake(220, 35))
    print("    ^ no class was edited, no subclass was written, nothing")
    print("      inherited changed. That swap has no equivalent on the")
    print("      inheritance side without defining a new subclass.")


if __name__ == "__main__":
    main()
