"""Exercise 4 — the trend sign is chosen by the start date.

One series, three fitted slopes. The full series is flat. Its first half
falls hard, its second half rises hard. Any of the three is a true
statement about a window; only one of them is a true statement about the
series, and the chart is what decides which one the reader gets.
"""

import pandas as pd

import honesty as H


def main():
    values = H.dipping_series()
    dates = pd.date_range("2025-01-06", periods=len(values), freq="W-MON")
    frame = pd.DataFrame({"date": dates, "value": values})

    half = len(values) // 2
    windows = {
        "full series": frame,
        "first half only": frame.iloc[:half],
        "second half only": frame.iloc[half:],
    }

    print(f"One weekly series, {len(values)} points, pandas {pd.__version__}.")
    print()
    print("  window              from         to           slope per week")
    slopes = {}
    for name, chunk in windows.items():
        slope = H.trend_slope(chunk["value"].to_numpy())
        slopes[name] = slope
        start = chunk["date"].iloc[0].date()
        end = chunk["date"].iloc[-1].date()
        print(f"  {name:<18}  {start}   {end}   {slope:+.4f}")
    print()

    first = slopes["first half only"]
    second = slopes["second half only"]
    full = slopes["full series"]

    assert first < 0 < second, (first, second)
    assert abs(full) < 0.05, full
    assert abs(first) > 0.5 and abs(second) > 0.5, (first, second)

    print("  The sign flips between the two halves, and the full series is")
    print(f"  flat ({full:+.4f} per week). Three honest sentences:")
    print(f"    {'declining at %.2f a week' % abs(first):<32} -- true of the first half")
    print(f"    {'growing at %.2f a week' % second:<32} -- true of the second half")
    print(f"    {'essentially unchanged':<32} -- true of the whole thing")
    print()
    print("  The defence is not a rule about slopes. It is a rule about the")
    print("  picture: show the full series, and mark the window you are")
    print("  talking about inside it.")
    print()
    print("04_cherry_picked_window.py: every assertion held.")


if __name__ == "__main__":
    main()
