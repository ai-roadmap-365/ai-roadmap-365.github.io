"""tiny_orm.py — a working object-relational mapper in under a hundred lines.

Build this before you touch SQLAlchemy. Everything the real library does is
here in miniature: columns declared as class attributes, DDL and DML generated
from that declaration, rows mapped back into objects, and an identity map so
that the same row fetched twice yields the *same* Python object.

Nothing here is clever. That is the point: once you have written the toy, the
real library stops being magic and becomes a much more careful version of code
you already understand.

Every statement this module emits is recorded on the session, so the tests can
assert on what was sent to the database rather than on what you hoped was sent.
"""

from __future__ import annotations

import sqlite3


class Column:
    """One mapped column. Declared as a class attribute on a Model subclass."""

    def __init__(self, sql_type: str, primary_key: bool = False) -> None:
        self.sql_type = sql_type
        self.primary_key = primary_key
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        # Python calls this at class-creation time and hands us the attribute
        # name, so a column never has to repeat its own name.
        self.name = name


class ModelMeta(type):
    """Collects the Column attributes of each subclass into __columns__."""

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__columns__ = {
            key: value for key, value in namespace.items() if isinstance(value, Column)
        }
        return cls


class Model(metaclass=ModelMeta):
    """Base class for mapped objects. Subclasses set __table__ and Columns."""

    __table__: str = ""

    def __init__(self, **values) -> None:
        unknown = set(values) - set(type(self).__columns__)
        if unknown:
            raise TypeError(f"{type(self).__name__} has no column(s): {sorted(unknown)}")
        for column_name in type(self).__columns__:
            # A plain instance attribute shadows the Column class attribute,
            # which is the whole trick: after __init__, obj.title is the value.
            setattr(self, column_name, values.get(column_name))

    @classmethod
    def primary_key_name(cls) -> str:
        for column_name, column in cls.__columns__.items():
            if column.primary_key:
                return column_name
        raise TypeError(f"{cls.__name__} declares no primary key")

    @classmethod
    def create_table_sql(cls) -> str:
        pieces = []
        for column_name, column in cls.__columns__.items():
            piece = f"{column_name} {column.sql_type}"
            if column.primary_key:
                piece += " PRIMARY KEY"
            pieces.append(piece)
        return f"CREATE TABLE {cls.__table__} ({', '.join(pieces)})"

    def __repr__(self) -> str:
        shown = ", ".join(
            f"{name}={getattr(self, name)!r}" for name in type(self).__columns__
        )
        return f"{type(self).__name__}({shown})"


class Session:
    """A unit of work: pending objects, an identity map, and a flush."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.identity_map: dict[tuple[type, object], Model] = {}
        self.pending: list[Model] = []
        self.statements: list[str] = []

    def execute(self, sql: str, parameters: tuple = ()) -> sqlite3.Cursor:
        self.statements.append(sql)
        return self.connection.execute(sql, parameters)

    def create_all(self, *model_classes: type[Model]) -> None:
        for model_class in model_classes:
            self.execute(model_class.create_table_sql())

    def add(self, instance: Model) -> None:
        """Make the object pending. No SQL is emitted here — that is the point."""
        self.pending.append(instance)

    def flush(self) -> None:
        """Turn every pending object into an INSERT. Still no commit."""
        for instance in self.pending:
            model_class = type(instance)
            column_names = list(model_class.__columns__)
            placeholders = ", ".join("?" for _ in column_names)
            sql = (
                f"INSERT INTO {model_class.__table__} "
                f"({', '.join(column_names)}) VALUES ({placeholders})"
            )
            values = tuple(getattr(instance, name) for name in column_names)
            cursor = self.execute(sql, values)
            key_name = model_class.primary_key_name()
            if getattr(instance, key_name) is None:
                setattr(instance, key_name, cursor.lastrowid)
            self.identity_map[(model_class, getattr(instance, key_name))] = instance
        self.pending.clear()

    def commit(self) -> None:
        self.flush()
        self.connection.commit()
        self.statements.append("COMMIT")

    def _instance_from_row(self, model_class: type[Model], row: tuple) -> Model:
        column_names = list(model_class.__columns__)
        values = dict(zip(column_names, row))
        key = (model_class, values[model_class.primary_key_name()])
        if key in self.identity_map:
            return self.identity_map[key]
        instance = model_class(**values)
        self.identity_map[key] = instance
        return instance

    def get(self, model_class: type[Model], key_value) -> Model | None:
        """Fetch by primary key. A hit in the identity map emits NO SQL."""
        key = (model_class, key_value)
        if key in self.identity_map:
            return self.identity_map[key]
        column_names = ", ".join(model_class.__columns__)
        sql = (
            f"SELECT {column_names} FROM {model_class.__table__} "
            f"WHERE {model_class.primary_key_name()} = ?"
        )
        row = self.execute(sql, (key_value,)).fetchone()
        if row is None:
            return None
        return self._instance_from_row(model_class, row)

    def select(self, model_class: type[Model], **equals) -> list[Model]:
        column_names = ", ".join(model_class.__columns__)
        sql = f"SELECT {column_names} FROM {model_class.__table__}"
        if equals:
            sql += " WHERE " + " AND ".join(f"{name} = ?" for name in equals)
        rows = self.execute(sql, tuple(equals.values())).fetchall()
        return [self._instance_from_row(model_class, row) for row in rows]
