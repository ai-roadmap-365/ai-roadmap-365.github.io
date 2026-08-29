# Troubleshooting -- Day 135 lab

Every symptom below was produced on the authoring machine at least once
while building this lab. The fixes are the real ones.

## Installation and tooling

**`ModuleNotFoundError: No module named 'pandas'`**
The interpreter running your script is not the one pandas is installed in.
Check which is which:

```bash
which python3
.venv/bin/python3 -c "import pandas, sys; print(pandas.__version__, sys.executable)"
```

Run everything with the virtual environment's interpreter, or activate the
environment first. `tests/run_tests.sh` sidesteps this by resolving
`python3` from the same directory as the `pytest` it found.

**`FAIL: pytest not found.`**
The runner looked in `$PYTEST`, then `.venv/bin/`, then `PATH`, and found
nothing. Create the environment as the README says, or run
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

**`ModuleNotFoundError: No module named 'api_server'`**
pytest was run from outside the lab directory, or `starter/conftest.py` is
missing from your copy. Run `pytest starter` or `pytest examples` from the
lab directory itself, not with a bare path to one file from somewhere else.

## The server

**`OSError: [Errno 48] Address already in use`**
This should be impossible here, because the lab binds port `0` and lets the
operating system choose. If you see it, you have edited a port number into
`api_server.py`. Put the `0` back.

**Tests hang for five seconds and then say the server never became ready.**
`wait_until_accepting` polls the port and gives up after five seconds.
Either the server thread crashed at start-up (run
`python3 examples/api_server.py` on its own and read the traceback), or
something on your machine is blocking loopback connections -- some
endpoint-security products do this.

**A stray Python process is left running after a failed test.**
It should not be: `running_server` is a context manager, the server thread
is a daemon thread, and `shutdown()`/`server_close()` run in a `finally`.
If you interrupted a run mid-start with Ctrl-C, check with
`ps aux | grep api_server` and stop it by hand.

## The grain trap and json_normalize

**`KeyError: 'orders'` from `json_normalize(..., record_path="orders")`**
Every record passed in must have an `orders` key, even if it is an empty
list. A record missing the key entirely (not just empty) raises this. Check
your payload with `[r.get("orders") for r in customers]` before calling
`json_normalize`.

**My "customer-grain" sum matches the inflated total, not the true one.**
You almost certainly called `flatten_order_grain` (which uses
`record_path="orders"`) where you meant `flatten_customer_grain` (which
calls `json_normalize` with no `record_path` at all). The order-grain frame
is *supposed* to inflate a customer-level sum -- that is exercise 1's whole
point -- so if a customer-level total looks too high, check which
flattening produced the frame you are summing.

**`explode` gave me fewer rows than I expected.**
Check whether the column actually holds Python lists, or JSON-encoded
strings that merely *look* like lists (`"['vip']"` instead of `['vip']`).
`explode` only expands real list objects; a string survives as one row
unchanged. This happens most often when a frame was round-tripped through
CSV, which this lab's JSONL raw storage avoids on purpose.

## Dtypes and drift

**`pin_dtypes` returned `coerced=0` even though the column looks numeric.**
`pandas.to_numeric` only counts a cell as coerced if it changed from a
non-numeric type. If your amounts already arrived as Python `float` (not
`str`) -- for example because you built a payload by hand with numeric
literals instead of quoted strings -- there is nothing to coerce, and 0 is
the correct answer, not a bug.

**`detect_schema_drift` reports a field that is present on every page.**
Check that you are passing a list of *pages*, each itself a list of
records (`list[list[dict]]`), not one flattened list of every record. A
field that is genuinely present everywhere should never appear in the
returned dict; if it does, the page boundaries you passed in do not match
the ones the API actually returned.

## The contract

**`check_contract` raises on a frame you believe is fine.**
Read the exact message -- it names the first rule broken, in a fixed
order: missing columns, then duplicate keys, then a non-numeric balance
column, then a negative balance, then row-count bounds. If you expected a
different rule to fire, check whether an earlier one in that order is also
broken; only the first violation is ever reported.

**`total_amount_due is not numeric -- pin_dtypes must run first`**
`check_contract` refuses to guess whether a string like `"500.00"` is a
valid balance. Call `pin_dtypes` on the assembled frame before checking the
contract -- the ordering (assemble, then pin, then check) is the discipline
this lesson is asking you to build, not an implementation detail.

## Idempotence and the incremental fetch

**`upsert` run twice gives me different row counts.**
Check that `key` names a column that is genuinely unique per real-world
entity in both frames -- `customer_id`, not something like `name` that two
different customers might share. `upsert` trusts the key you give it.

**My second incremental call returns nothing at all, even though I expect
the boundary record back.**
Confirm you are passing the boundary with `>=` semantics, matching
`fetch_incremental`'s own convention (`since` is inclusive). A client-side
filter that turns it into `>` will silently drop the boundary record --
which is exactly the off-by-one the lesson names, and exactly why this lab
chose the other side of it.
