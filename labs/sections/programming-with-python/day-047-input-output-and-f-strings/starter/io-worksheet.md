# Day 047 worksheet — Input, Output, and f-strings

Fill this in from your own runs as you complete `io_demo.py`. Copy real values
straight from your terminal — the point is to *see* the behavior, not guess it.

## 1. Proof that `input()` returns a string

Run this in a Python shell (`python3`), type `5` when prompted, and record what
you see:

```python
x = input("x: ")
type(x)      # what does this report?  __________________
x            # what value is x?         __________________
x + x        # what does this print?    __________________  (why is it not 10?)
```

- `type(input("x: "))` reports: `______________________`
- Typing `5` gives the value: `______________________`
- One sentence, in your own words, on why `input()` returns text and not a number:
  `______________________________________________________________________`

## 2. The format spec you used

Write the exact f-string spec you used to right-align a number to two decimals
in a fixed-width column, and label each part:

- Spec: `f"{value:__________}"`
- The alignment character is `____` and it means `______________________`
- The width is `____` and it means `______________________`
- The `.2f` part means `______________________`

## 3. What your finished program prints

Run your completed program on the input `8 3` **both ways** and paste the output:

```text
$ python3 starter/io_demo.py 8 3
______________________________________________
______________________________________________
______________________________________________
______________________________________________
______________________________________________
______________________________________________

$ echo "8 3" | python3 starter/io_demo.py
(should be identical to the line above)
```

## 4. Why errors go to standard error

In two or three sentences, explain why `io_demo.py` prints its error message to
**standard error** instead of standard output, and what would go wrong in a
pipeline like `python3 io_demo.py | sort` if the error went to standard output
instead:

```
____________________________________________________________________________
____________________________________________________________________________
____________________________________________________________________________
```
