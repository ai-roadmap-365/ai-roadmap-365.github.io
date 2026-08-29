# Debug worksheet — Day 048

Fill this in as you fix each program in `starter/`. Run each one with
`python3 <file>.py`, read the traceback **bottom-up**, then complete the row.

## For each program

| Program | Exception type | Line number | Cause (why the value was wrong) | Your fix |
| --- | --- | --- | --- | --- |
| `average_scores.py` |  |  |  |  |
| `lookup_capital.py` |  |  |  |  |
| `total_price.py` |  |  |  |  |

Example of a completed row (do not copy — investigate for yourself):

| Program | Exception type | Line number | Cause | Your fix |
| --- | --- | --- | --- | --- |
| `demo.py` | `ZeroDivisionError: division by zero` | 4 | `values` was an empty list, so `len(values)` was 0 | guard the empty case before dividing |

## How the three bugs differ

Write 4–6 sentences below: what category of mistake each bug represents (a
bad index, a missing key, a type mismatch), and how the exception type alone
told you which kind of fix each one needed.

_Your paragraph here._
