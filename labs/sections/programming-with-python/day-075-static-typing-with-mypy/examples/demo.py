"""A deterministic tour of the fixed catalogue.

    python3 examples/demo.py

Every line printed here is fixed text or arithmetic — no clocks, no random
numbers, no memory addresses — so it matches expected-output/sample-run.txt
character for character.
"""

from __future__ import annotations

from pathlib import Path

import catalog

HERE = Path(__file__).resolve().parent


def main() -> None:
    print("1. The lookup that can fail")
    print("---------------------------")
    print(f"find_model('small'):    {catalog.find_model('small')}")
    print(f"find_model('enormous'): {catalog.find_model('enormous')}")
    print()

    print("2. describe() — the function the tests never asked about")
    print("--------------------------------------------------------")
    print(f"describe('small'):    {catalog.describe('small')}")
    print(f"describe('large'):    {catalog.describe('large')}")
    print(f"describe('enormous'): {catalog.describe('enormous')}")
    print("  ^ the buggy version raised AttributeError on that last line")
    print()

    print("3. split_cost() — an int really is an int now")
    print("---------------------------------------------")
    print(f"split_cost('medium', 1000000, 2): {catalog.split_cost('medium', 1_000_000, 2)}")
    print(f"split_cost('medium', 1000000, 3): {catalog.split_cost('medium', 1_000_000, 3)}")
    print("  ^ 1000000 // 3 is 333333 tokens; 1000000 / 3 would have been 333333.33...")
    print()

    print("4. price_line() — an annotated helper, callable under strict")
    print("------------------------------------------------------------")
    for name in ("small", "medium", "large"):
        print(f"  {catalog.price_line(name)}")
    print(f"  {catalog.price_line('enormous')}")
    print()

    print("5. load_settings() — checked at the boundary, not merely annotated")
    print("------------------------------------------------------------------")
    settings = catalog.load_settings(str(HERE / "settings.json"))
    for key in sorted(settings):
        print(f"  {key} = {settings[key]!r}")
    print("  every value is a real float, because the loader converted it")


if __name__ == "__main__":
    main()
