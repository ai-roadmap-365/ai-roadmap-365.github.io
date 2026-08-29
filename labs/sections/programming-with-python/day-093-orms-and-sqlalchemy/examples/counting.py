"""counting.py — record every statement the engine sends to the database.

This is the instrument the whole lab is built around. The ORM's promise is that
you write Python and it writes SQL; the only way to hold it to that promise is
to look at the SQL. SQLAlchemy exposes a `before_cursor_execute` event on the
Engine, which fires once per statement actually sent to the DBAPI cursor, and
that is exactly the granularity a query count wants.

Why count statements rather than time them: a timing assertion is a flake
waiting for a slow machine, and it tells you nothing about the cause. A count
is deterministic, it is the same number on every machine, and it names the
defect directly — "this loop issued fifty-one queries" is a bug report, while
"this loop took 240 milliseconds" is a mood.
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.engine import Engine


def normalise(statement: str) -> str:
    """Collapse SQLAlchemy's multi-line SQL into one comparable line."""
    return " ".join(statement.split())


class QueryCounter:
    """Context manager recording every statement an Engine emits.

    Usage:

        with QueryCounter(engine) as counted:
            ...do ORM work...
        print(len(counted), counted.selects())
    """

    def __init__(self, engine: Engine, seed: bool = False) -> None:
        self.engine = engine
        self.statements: list[str] = []
        self.batched: list[bool] = []
        self.parameter_sets: list[int] = []
        self._seed = seed

    def _record(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(normalise(statement))
        self.batched.append(bool(executemany))
        # How many rows this one cursor execution carries. An executemany hands
        # the driver a sequence of parameter tuples; a normal execute hands it
        # one. Counting both numbers is what stops "one statement" from being
        # mistaken for "one row".
        if executemany:
            try:
                self.parameter_sets.append(len(parameters))
            except TypeError:
                self.parameter_sets.append(1)
        else:
            self.parameter_sets.append(1)

    def __enter__(self) -> QueryCounter:
        event.listen(self.engine, "before_cursor_execute", self._record)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        event.remove(self.engine, "before_cursor_execute", self._record)
        return False

    def __len__(self) -> int:
        """Cursor executions — the number of round trips to the driver."""
        return len(self.statements)

    def rows_sent(self) -> int:
        """Parameter sets across every execution: how many rows were carried."""
        return sum(self.parameter_sets)

    def executemany_count(self) -> int:
        """How many of the executions were batched executemany calls."""
        return sum(1 for flag in self.batched if flag)

    def starting_with(self, keyword: str) -> list[str]:
        upper = keyword.upper()
        return [s for s in self.statements if s.upper().startswith(upper)]

    def selects(self) -> list[str]:
        return self.starting_with("SELECT")

    def inserts(self) -> list[str]:
        return self.starting_with("INSERT")

    def updates(self) -> list[str]:
        return self.starting_with("UPDATE")

    def report(self, indent: str = "    ") -> str:
        if not self.statements:
            return f"{indent}(no statements)"
        lines = []
        for number, statement in enumerate(self.statements, start=1):
            shown = statement if len(statement) <= 110 else statement[:107] + "..."
            lines.append(f"{indent}{number:>2}. {shown}")
        return "\n".join(lines)
