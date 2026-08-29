"""Step 2: predict the MRO of a diamond, then check yourself.

BEFORE RUNNING THIS, write your prediction down on paper.

The hierarchy is a diamond: ToasterOven inherits from Heater and Timer, and
both of those inherit from Appliance. C3 linearization gives exactly one
order, and it guarantees two things you can re-derive by hand:

  * local precedence — a class always comes before its own parents;
  * monotonicity     — the order bases are listed in is preserved.

So: start at ToasterOven. Bases are (Heater, Timer), so Heater is next.
Heater's parent is Appliance — but Appliance cannot come yet, because Timer
also inherits from it and Timer must precede its own parent. So Timer, then
Appliance, then object. Appliance appears ONCE, which is why it is never
initialised or run twice.

Run it:  python3 examples/02_mro_diamond.py
"""


class Appliance:
    def power_on(self):
        return "Appliance: power on"


class Heater(Appliance):
    def power_on(self):
        return "Heater: elements warming -> " + super().power_on()


class Timer(Appliance):
    def power_on(self):
        return "Timer: clock started -> " + super().power_on()


class ToasterOven(Heater, Timer):
    def power_on(self):
        return "ToasterOven: ready -> " + super().power_on()


def main():
    print(" -> ".join(cls.__name__ for cls in ToasterOven.__mro__))
    print(ToasterOven().power_on())
    print()

    # The payoff: super() is NOT "my parent". It is "the next class in THIS
    # instance's MRO". Heater does not inherit from Timer and has never heard
    # of it, yet Heater's super() call lands there.
    mro = [cls.__name__ for cls in ToasterOven.__mro__]
    after_heater = mro[mro.index("Heater") + 1]
    print(f"Heater's super() lands on: {after_heater}")
    print(f"Heater actually inherits from: "
          f"{[c.__name__ for c in Heater.__bases__]}")
    print(f"Appliance appears in the MRO {mro.count('Appliance')} time(s) — "
          f"never run twice.")

    # If no consistent order exists, Python refuses at class-definition time
    # rather than guessing. Here the bases are listed parent-before-child.
    print()
    try:
        type("Impossible", (Appliance, Heater), {})
    except TypeError as err:
        print(f"TypeError: {err}")


if __name__ == "__main__":
    main()
