"""A matrix built from first principles, on nothing but nested lists.

This is the reference implementation the lab's tests assert against, and the
thing NumPy is compared to. It deliberately implements only five ideas:

    * shape, as a (rows, columns) tuple;
    * indexing with a (row, column) pair, counting from zero;
    * transpose, which swaps the two axes;
    * addition, which is elementwise and requires identical shapes;
    * scalar multiplication, which multiplies every entry by one number.

It deliberately does NOT implement broadcasting. That omission is the point
of the last exercise: broadcasting is the first thing on this list that is
genuinely difficult to write and genuinely easy to misuse, and seeing the
gap is how you learn what NumPy is doing for you.

Every operation returns a NEW Matrix. Nothing here mutates in place, which
makes the class boring and safe, and makes the contrast with NumPy views
(where mutation travels) sharper in exercise 4.
"""

from __future__ import annotations


class ShapeMismatch(ValueError):
    """Raised when two matrices cannot be combined because their shapes differ.

    A subclass of ValueError on purpose: NumPy raises ValueError for the same
    situation, so code that catches ValueError catches both. The tests assert
    that relationship rather than assuming it.
    """


class Matrix:
    """A rectangular grid of numbers, stored as a list of row lists."""

    def __init__(self, rows):
        rows = [list(row) for row in rows]
        if not rows:
            raise ValueError("a matrix needs at least one row")
        width = len(rows[0])
        if width == 0:
            raise ValueError("a matrix needs at least one column")
        for i, row in enumerate(rows):
            if len(row) != width:
                raise ValueError(
                    f"row {i} has {len(row)} entries but row 0 has {width}; "
                    "a matrix is rectangular, so every row must be the same length"
                )
        self._rows = rows

    # -- shape ------------------------------------------------------------

    @property
    def shape(self):
        """(rows, columns) — rows first, because that is the convention."""
        return (len(self._rows), len(self._rows[0]))

    @property
    def n_rows(self):
        return self.shape[0]

    @property
    def n_cols(self):
        return self.shape[1]

    # -- indexing ---------------------------------------------------------

    def __getitem__(self, position):
        """m[i, j] — row i, column j, both counting from 0."""
        i, j = self._check_position(position)
        return self._rows[i][j]

    def __setitem__(self, position, value):
        i, j = self._check_position(position)
        self._rows[i][j] = value

    def _check_position(self, position):
        if not isinstance(position, tuple) or len(position) != 2:
            raise TypeError(
                "index a Matrix with a (row, column) pair, for example m[0, 2]"
            )
        i, j = position
        n_rows, n_cols = self.shape
        if not (0 <= i < n_rows) or not (0 <= j < n_cols):
            raise IndexError(
                f"position {position} is outside a matrix of shape {self.shape}; "
                f"valid rows are 0..{n_rows - 1} and valid columns are 0..{n_cols - 1}"
            )
        return i, j

    def row(self, i):
        """Row i as a plain list — a copy, so editing it changes nothing here."""
        return list(self._rows[i])

    def col(self, j):
        """Column j as a plain list. Note this has to walk every row."""
        return [row[j] for row in self._rows]

    # -- operations -------------------------------------------------------

    def transpose(self):
        """Swap rows and columns: an (r, c) matrix becomes (c, r)."""
        n_rows, n_cols = self.shape
        return Matrix([[self._rows[i][j] for i in range(n_rows)] for j in range(n_cols)])

    @property
    def T(self):
        """Spelled the way NumPy spells it, so the comparison reads cleanly."""
        return self.transpose()

    def add(self, other):
        """Elementwise addition. Both shapes must match exactly — no broadcasting."""
        if not isinstance(other, Matrix):
            raise TypeError(
                "add expects another Matrix; this class has no broadcasting, "
                "so a plain number or a list is not accepted"
            )
        if self.shape != other.shape:
            raise ShapeMismatch(
                f"cannot add {self.shape} to {other.shape}: "
                "addition here is entry by entry, so the shapes must be identical"
            )
        n_rows, n_cols = self.shape
        return Matrix(
            [[self[i, j] + other[i, j] for j in range(n_cols)] for i in range(n_rows)]
        )

    def __add__(self, other):
        return self.add(other)

    def scale(self, k):
        """Multiply every entry by the number k."""
        n_rows, n_cols = self.shape
        return Matrix([[self[i, j] * k for j in range(n_cols)] for i in range(n_rows)])

    def __mul__(self, k):
        return self.scale(k)

    __rmul__ = __mul__

    def apply_to(self, vector):
        """Treat the matrix as a transformation and apply it to one vector.

        Each output entry is the sum of one row multiplied entry by entry
        against the input vector. An (r, c) matrix therefore eats a vector of
        length c and returns a vector of length r.

        This is written out as an explicit double loop on purpose: the packed
        name for it, and the operator NumPy spells `@`, is Day 101's subject.
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

    # -- constructors for the matrices worth recognising on sight ---------

    @classmethod
    def zeros(cls, n_rows, n_cols):
        return cls([[0] * n_cols for _ in range(n_rows)])

    @classmethod
    def identity(cls, n):
        """The matrix that leaves every vector exactly as it found it."""
        return cls([[1 if i == j else 0 for j in range(n)] for i in range(n)])

    @classmethod
    def diagonal(cls, values):
        values = list(values)
        n = len(values)
        return cls([[values[i] if i == j else 0 for j in range(n)] for i in range(n)])

    # -- reporting --------------------------------------------------------

    def is_symmetric(self):
        """True when the matrix equals its own transpose. Requires squareness."""
        n_rows, n_cols = self.shape
        if n_rows != n_cols:
            return False
        return all(
            self[i, j] == self[j, i] for i in range(n_rows) for j in range(n_cols)
        )

    def to_lists(self):
        """A plain nested list — the shape numpy.array() wants."""
        return [list(row) for row in self._rows]

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __repr__(self):
        body = ", ".join(repr(row) for row in self._rows)
        return f"Matrix([{body}])  # shape {self.shape}"

    def format(self, width=4):
        """A readable grid, one row per line, right-aligned in fixed columns."""
        return "\n".join(
            " ".join(f"{value:>{width}}" for value in row) for row in self._rows
        )
