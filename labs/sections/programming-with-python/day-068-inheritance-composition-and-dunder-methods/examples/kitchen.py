"""Reference implementation: a container class that plain Python accepts.

Step 4 of the Day 068 lab, "Protocols and Hierarchies".

`Menu` is an ordinary class holding `Dish` objects. It inherits from nothing
but `object`. Every capability below comes from implementing a dunder method
that the interpreter already knows how to call:

    len(menu)          -> Menu.__len__
    menu[0], menu[1:]  -> Menu.__getitem__
    for dish in menu   -> Menu.__iter__
    "Ramen" in menu    -> Menu.__contains__
    a == b             -> Menu.__eq__      (and __hash__, which it would break)
    sorted(menus)      -> Menu.__lt__      (via @total_ordering)
    with menu:         -> Menu.__enter__ / Menu.__exit__

The point of the demo at the bottom is that `sorted`, `max`, `list`, `set`,
`len`, `in` and the `for` statement are all UNMODIFIED — they were written
long before this file existed. They work because of the protocols, not
because of anything they know about `Menu`.

Run it directly:  python3 examples/kitchen.py
"""

from functools import total_ordering


class Dish:
    """One dish: a name and how many minutes it takes to prepare."""

    def __init__(self, name, minutes):
        self.name = name
        self.minutes = minutes

    def __repr__(self):
        # The unambiguous developer form, used inside containers too.
        return f"Dish({self.name!r}, {self.minutes})"

    def __eq__(self, other):
        # Return NotImplemented (not False) for types we do not know, so the
        # other operand still gets its chance to answer.
        if not isinstance(other, Dish):
            return NotImplemented
        return (self.name, self.minutes) == (other.name, other.minutes)

    def __hash__(self):
        # Required: defining __eq__ sets __hash__ to None. Hash the same
        # fields __eq__ compares, so equal dishes hash equal.
        return hash((self.name, self.minutes))


@total_ordering
class Menu:
    """A collection of dishes that behaves like a built-in collection."""

    def __init__(self, name, dishes=None):
        self.name = name
        self.dishes = list(dishes or [])
        self.open = False

    def __repr__(self):
        return f"Menu({self.name!r}, {len(self.dishes)} dishes)"

    # --- Exercise 1: sizing -------------------------------------------------
    def __len__(self):
        return len(self.dishes)

    # --- Exercise 2: indexing ----------------------------------------------
    def __getitem__(self, index):
        # Delegating to the list means slices work for free: a slice object
        # passed to list.__getitem__ returns a list.
        return self.dishes[index]

    # --- Exercise 3: iteration ---------------------------------------------
    def __iter__(self):
        return iter(self.dishes)

    # --- Exercise 4: membership --------------------------------------------
    def __contains__(self, item):
        # Accept either a Dish or a plain name string.
        name = item.name if isinstance(item, Dish) else item
        return any(dish.name == name for dish in self.dishes)

    def total_minutes(self):
        return sum(dish.minutes for dish in self.dishes)

    # --- Exercise 5: equality (and the hash it would otherwise break) ------
    def __eq__(self, other):
        if not isinstance(other, Menu):
            return NotImplemented
        return self.dishes == other.dishes

    def __hash__(self):
        return hash(tuple(self.dishes))

    # --- Exercise 6: ordering ----------------------------------------------
    def __lt__(self, other):
        # @total_ordering derives <=, > and >= from __lt__ plus __eq__.
        if not isinstance(other, Menu):
            return NotImplemented
        return self.total_minutes() < other.total_minutes()

    # --- Context manager protocol (step 5 of the lab) ----------------------
    def __enter__(self):
        self.open = True
        print(f"[service open] {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Runs on the way out whether the block succeeded or raised.
        self.open = False
        print(f"[service closed] {self.name}")
        return False  # False = do not swallow the exception


def build_menus():
    """The three menus the demo and the tests both use."""
    lunch = Menu("Lunch", [Dish("Ramen", 12), Dish("Gyoza", 8), Dish("Salad", 4)])
    dinner = Menu("Dinner", [Dish("Ramen", 12), Dish("Duck", 40)])
    # An independent Menu holding equal dishes — a different object, equal value.
    copy = Menu("Lunch copy", [Dish("Ramen", 12), Dish("Gyoza", 8), Dish("Salad", 4)])
    return lunch, dinner, copy


def demo():
    """Prove that unmodified builtins work on a class written this afternoon."""
    lunch, dinner, copy = build_menus()

    print(f"len: {len(lunch)}")
    print(f"index: {lunch[0]!r} | slice: {lunch[1:3]!r}")
    print(f"iterate: {[dish.name for dish in lunch]}")
    print(f"contains: {'Ramen' in lunch} | {'Duck' in lunch}")
    print(f"equal: {lunch == copy} | {lunch == dinner}")
    print(f"eq other type: {lunch == 'Lunch'}")
    print(f"hash equal: {hash(lunch) == hash(copy)}")
    print(f"lt: {dinner < lunch} | ge (total_ordering): {dinner >= lunch}")
    print(f"sorted: {sorted([dinner, lunch])!r}")
    print(f"max: {max([dinner, lunch], key=len)!r}")
    print(f"longest dish: {max(lunch, key=lambda dish: dish.minutes)!r}")
    print(f"sum minutes via comprehension: {sum(dish.minutes for dish in lunch)}")
    print(f"set of menus: {len({lunch, copy, dinner})}")
    print(f"list(): {len(list(dinner))}")


if __name__ == "__main__":
    demo()
