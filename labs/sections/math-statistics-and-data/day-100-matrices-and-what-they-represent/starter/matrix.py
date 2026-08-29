"""Exercise 1 — build the matrix yourself, on nothing but nested lists.

Fill in the five methods marked EXERCISE below. Each one is a few lines. The
point is not difficulty; it is that after writing them you will never again be
unsure what `.shape`, `.T` or an elementwise sum is actually doing, because you
will have done it.

Check your work as you go, from the LAB DIRECTORY (one level up from here):

    .venv/bin/pytest starter -q

Every test for a method you have not written yet is skipped, not failed, so the
output is a running score rather than a wall of red. When all of them pass,
compare your file with examples/matrix.py — they should agree on behaviour,
not necessarily on wording.

Rules for all five: return a NEW Matrix, never modify self, and do not import
numpy in this file. The whole value of the exercise is that nothing here is
done for you.
"""

from __future__ import annotations


class ShapeMismatch(ValueError):
    """Raised when two matrices cannot be combined because their shapes differ.

    Subclassing ValueError is deliberate: NumPy raises ValueError for the same
    situation, so one `except ValueError` catches your class and NumPy alike.
    """


class Matrix:
    """A rectangular grid of numbers, stored as a list of row lists."""

    def __init__(self, rows):
        rows = [list(row) for row in rows]
        if not rows or not rows[0]:
            raise ValueError("a matrix needs at least one row and one column")
        width = len(rows[0])
        for i, row in enumerate(rows):
            if len(row) != width:
                raise ValueError(
                    f"row {i} has {len(row)} entries but row 0 has {width}; "
                    "a matrix is rectangular"
                )
        self._rows = rows

    # ---------------------------------------------------------------- 1.1 --
    @property
    def shape(self):
        """EXERCISE 1.1 — return (number of rows, number of columns).

        Rows first. That order is a convention rather than a law, and it is
        worth saying out loud once so you never have to wonder again.

        Hint: len(self._rows) and len(self._rows[0]).
        """
        raise NotImplementedError("write Matrix.shape")

    # ---------------------------------------------------------------- 1.2 --
    def __getitem__(self, position):
        """EXERCISE 1.2 — support m[i, j], counting rows and columns from 0.

        `position` arrives as a tuple (i, j). Two requirements beyond the
        obvious lookup:

          * if `position` is not a 2-tuple, raise TypeError with a message
            that says how to index a Matrix;
          * if i or j is outside the matrix, raise IndexError with a message
            that includes the string f"shape {self.shape}" — the tests check
            for exactly that, because an error that does not tell you the
            shape makes you go and print it yourself.

        Note that negative indices should be rejected too: Python lists accept
        m[-1], and a matrix that silently wraps around is a bug generator.
        """
        raise NotImplementedError("write Matrix.__getitem__")

    def row(self, i):
        """Row i as a plain list. Already written, and it copies on purpose."""
        return list(self._rows[i])

    def col(self, j):
        """Column j as a plain list. Note that this has to walk every row."""
        return [row[j] for row in self._rows]

    # ---------------------------------------------------------------- 1.3 --
    def transpose(self):
        """EXERCISE 1.3 — swap rows and columns; (r, c) becomes (c, r).

        Entry (i, j) of the result is entry (j, i) of the original. A nested
        list comprehension does it in one line, but write it as two loops
        first if that reads more clearly to you.
        """
        raise NotImplementedError("write Matrix.transpose")

    @property
    def T(self):
        """Spelled the way NumPy spells it. Already written."""
        return self.transpose()

    # ---------------------------------------------------------------- 1.4 --
    def add(self, other):
        """EXERCISE 1.4 — elementwise addition, with no broadcasting at all.

          * if `other` is not a Matrix, raise TypeError, and say in the message
            that this class has no broadcasting;
          * if the shapes differ, raise ShapeMismatch naming both shapes;
          * otherwise return a new Matrix of the entrywise sums.
        """
        raise NotImplementedError("write Matrix.add")

    def __add__(self, other):
        return self.add(other)

    # ---------------------------------------------------------------- 1.5 --
    def scale(self, k):
        """EXERCISE 1.5 — multiply every entry by the single number k."""
        raise NotImplementedError("write Matrix.scale")

    def __mul__(self, k):
        return self.scale(k)

    __rmul__ = __mul__

    # ---------------------------------------------------------------- 1.6 --
    @classmethod
    def identity(cls, n):
        """EXERCISE 1.6 — the n by n matrix with 1 on the diagonal, 0 elsewhere.

        This is the matrix that leaves every vector exactly as it found it, and
        recognising it on sight is worth more than it looks.
        """
        raise NotImplementedError("write Matrix.identity")

    # -- already written, so you have something to test against -------------

    @classmethod
    def zeros(cls, n_rows, n_cols):
        return cls([[0] * n_cols for _ in range(n_rows)])

    def apply_to(self, vector):
        """Treat the matrix as a transformation and apply it to one vector.

        Each output entry is one row multiplied entry by entry against the
        input vector and then summed. An (r, c) matrix therefore eats a vector
        of length c and returns a vector of length r.

        Written for you because the packed name for it is Day 101's subject.
        """
        vector = list(vector)
        n_rows, n_cols = self.shape
        if len(vector) != n_cols:
            raise ShapeMismatch(
                f"a {self.shape} matrix transforms a vector of length {n_cols}, "
                f"but this vector has length {len(vector)}"
            )
        return [
            sum(self[i, j] * vector[j] for j in range(n_cols)) for i in range(n_rows)
        ]

    def to_lists(self):
        return [list(row) for row in self._rows]

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __repr__(self):
        body = ", ".join(repr(row) for row in self._rows)
        return f"Matrix([{body}])"

    def format(self, width=4):
        return "\n".join(
            " ".join(f"{value:>{width}}" for value in row) for row in self._rows
        )
