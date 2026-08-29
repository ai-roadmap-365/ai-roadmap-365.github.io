# Security notes — Day 069 lab

- **What the lab does:** defines classes, builds objects from literal values
  written into the source, serialises a couple of them to a JSON *string* in
  memory, and prints. It creates **no files**, makes **no network
  connections**, needs **no privileges**, and reads nothing outside its own
  directory. The test runner sets `PYTHONDONTWRITEBYTECODE=1` so it does not
  even leave a bytecode cache behind.

- **A type hint is not a validation, and must never be treated as one at a
  trust boundary.** This is the security lesson of the day. `score: float`
  is a claim about what *should* be there, recorded and never checked. A
  static checker cannot help either, because it reasons about your source
  code and never sees the value that actually arrived from a file, a request,
  or a model's response. Run `python3 examples/inspect_runtime.py` and watch
  a string land in a field annotated `float` with nothing raised. Annotate
  for clarity; validate for safety; never confuse the two.

- **`__post_init__` is the gate that actually runs.** If a record has a rule,
  that is where it belongs, because it executes on every construction —
  including the ones built from data you did not write:

  ```python
  def __post_init__(self) -> None:
      if not 0.0 <= self.score <= 1.0:
          raise ValueError(f"score must be between 0.0 and 1.0, got {self.score}")
  ```

  Validate once, at the edge, as the object is built. After that the rest of
  your program can trust the object instead of re-checking it at every use —
  and code that re-checks everywhere is code that will eventually forget to.

- **`Record(**row)` is only as safe as its validation.** Unpacking a
  dictionary that came from a file or a network response straight into a
  constructor is a convenient pattern and a common one, but every field
  arrives unchecked. Two things go wrong: unexpected keys raise `TypeError`
  (noisy, therefore fine), and *expected* keys holding wrong-typed values
  pass straight through (silent, therefore dangerous). `__post_init__` is
  what closes the second gap. For anything genuinely untrusted, a library
  such as pydantic — which enforces the annotations at runtime — is the
  right tool.

- **The generated `__repr__` prints every field, and reprs end up in logs.**
  A dataclass repr appears in tracebacks, debugger output, and any log line
  that formats the object. Put an API key, a token, a password, or a
  person's details in a dataclass and you have arranged for it to be printed
  the next time anything goes wrong — often into a log you forward somewhere
  else. The fix is one argument per field:

  ```python
  from dataclasses import dataclass, field

  @dataclass
  class Client:
      endpoint: str
      api_key: str = field(repr=False)
  ```

  Make a habit of asking, for every field you declare, whether you would be
  comfortable seeing it in a log line — because eventually you will.

- **`frozen=True` is a correctness guarantee, not a security boundary.** It
  stops accidental mutation, which is genuinely valuable: it is what makes a
  generated hash safe, and what stops one part of your program quietly
  changing a record another part is holding. It is not a defence against
  code that is actively trying to get past it, and it does not deep-freeze
  anything — a frozen dataclass holding a list still has a list you can
  append to. Immutability here means "the field cannot be reassigned", not
  "the contents cannot change".

- **Never rebuild objects from untrusted data with anything that executes
  it.** `asdict` has no automatic reverse, and that is a feature: you write
  the rebuild, so you decide which fields are accepted. Do that with
  `json.loads` and explicit field access, as `records_from_json` does in
  `examples/records.py`. Never use `eval()`, and never use `pickle` on data
  from outside your program — unpickling runs code by design, so a pickle
  file from an untrusted source is an executable, not a document. This
  matters more than it sounds: shared model and dataset artifacts are a
  place people still meet pickles in the wild.

- **Reading before running:** every file in this lab is short and commented.
  Read `examples/records.py`, `examples/mini_dataclass.py`, and
  `tests/run_tests.sh` before running them. Running unread scripts is one of
  the most common ways developers get compromised; the course's rule is that
  every lab script is small enough to read and understand first. Note in
  particular that `examples/check_types.sh` will execute a type checker if it
  finds one on your `PATH` — read that script and satisfy yourself about what
  it invokes and with what arguments before you install a checker and re-run
  it.
