"""YOUR COPY — complete the six numbered exercises.

This is a working skeleton. `Dish` is finished for you and the plumbing runs.
Six methods on `Menu` raise NotImplementedError on purpose; each one is a
numbered exercise telling you exactly what to write. Replace the `raise` with
your implementation, one at a time, running the file after each.

    python3 starter/kitchen.py

The demo at the bottom exercises `len()`, indexing, slicing, `for`, `in`,
`==`, `hash()`, `sorted()` and `max()`. None of those are modified in any
way — they are the builtins. When all six exercises are done, every one of
them will work on a class you wrote, and the output will match
`expected-output/sample-run.txt`.

Compare with `examples/kitchen.py` only after you have tried.
"""

from functools import total_ordering


class Dish:
    """Finished for you — study it, it is the pattern for exercise 5."""

    def __init__(self, name, minutes):
        self.name = name
        self.minutes = minutes

    def __repr__(self):
        return f"Dish({self.name!r}, {self.minutes})"

    def __eq__(self, other):
        # Note the NotImplemented return for unknown types: it tells Python
        # "ask the other operand", rather than answering False confidently.
        if not isinstance(other, Dish):
            return NotImplemented
        return (self.name, self.minutes) == (other.name, other.minutes)

    def __hash__(self):
        # Defining __eq__ sets __hash__ to None, so it must be restored here.
        return hash((self.name, self.minutes))


@total_ordering
class Menu:
    """A collection of dishes. Make plain Python accept it."""

    def __init__(self, name, dishes=None):
        self.name = name
        self.dishes = list(dishes or [])
        self.open = False

    def __repr__(self):
        return f"Menu({self.name!r}, {len(self.dishes)} dishes)"

    def total_minutes(self):
        """Finished for you — used by exercise 6."""
        return sum(dish.minutes for dish in self.dishes)

    # --- Exercise 1 --------------------------------------------------------
    # Make `len(menu)` work. Return how many dishes this menu holds.
    # Hint: `self.dishes` is a list; call the builtin `len()` on it.
    def __len__(self):
        raise NotImplementedError("Exercise 1: return len(self.dishes)")

    # --- Exercise 2 --------------------------------------------------------
    # Make `menu[0]` and `menu[1:3]` work. Return the item at `index`.
    # Hint: return `self.dishes[index]`. Because a list handles slice objects
    # itself, delegating like this makes slicing work with no extra code.
    def __getitem__(self, index):
        raise NotImplementedError("Exercise 2: return self.dishes[index]")

    # --- Exercise 3 --------------------------------------------------------
    # Make `for dish in menu:` work. Return an ITERATOR over the dishes.
    # Hint: `return iter(self.dishes)` — do not return the list itself, a
    # list is iterable but is not an iterator.
    def __iter__(self):
        raise NotImplementedError("Exercise 3: return iter(self.dishes)")

    # --- Exercise 4 --------------------------------------------------------
    # Make `"Ramen" in menu` work, accepting either a Dish or a plain name.
    # Hint: get the name with
    #   name = item.name if isinstance(item, Dish) else item
    # then return True if any dish in self.dishes has that name. A generator
    # expression inside the builtin `any()` reads well here.
    def __contains__(self, item):
        raise NotImplementedError("Exercise 4: any(dish.name == name for ...)")

    # --- Exercise 5 --------------------------------------------------------
    # Make `menu_a == menu_b` compare the dishes they hold. Two menus are
    # equal when their `dishes` lists are equal (Dish.__eq__ does the rest).
    # Return NotImplemented when `other` is not a Menu.
    #
    # THEN: because you defined __eq__, Python set __hash__ to None and your
    # menus became unhashable. Restore it below by hashing the same data
    # __eq__ compares — `hash(tuple(self.dishes))` works, because Dish is
    # hashable and a tuple of hashables is hashable.
    def __eq__(self, other):
        raise NotImplementedError("Exercise 5a: compare self.dishes")

    def __hash__(self):
        raise NotImplementedError("Exercise 5b: return hash(tuple(self.dishes))")

    # --- Exercise 6 --------------------------------------------------------
    # Make `sorted(menus)` work by defining ONE comparison. A menu sorts
    # before another when its total_minutes() is smaller. Return
    # NotImplemented when `other` is not a Menu.
    # The @total_ordering decorator above the class will then derive
    # <=, > and >= from this method plus __eq__ — so you write one, get four.
    def __lt__(self, other):
        raise NotImplementedError("Exercise 6: compare total_minutes()")

    # --- Finished for you: the context manager protocol (lab step 5) -------
    def __enter__(self):
        self.open = True
        print(f"[service open] {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.open = False
        print(f"[service closed] {self.name}")
        return False  # False = do not swallow the exception


def build_menus():
    """The three menus the demo and the tests both use."""
    lunch = Menu("Lunch", [Dish("Ramen", 12), Dish("Gyoza", 8), Dish("Salad", 4)])
    dinner = Menu("Dinner", [Dish("Ramen", 12), Dish("Duck", 40)])
    copy = Menu("Lunch copy", [Dish("Ramen", 12), Dish("Gyoza", 8), Dish("Salad", 4)])
    return lunch, dinner, copy


def demo():
    """Every line below is an UNMODIFIED builtin working on your class."""
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
