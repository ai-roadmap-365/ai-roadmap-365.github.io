"""models.py — the same library domain, mapped with SQLAlchemy 2.0.

This is the modern declarative style: a DeclarativeBase subclass, `Mapped[...]`
annotations, and `mapped_column()`. The 1.x `declarative_base()` factory and the
`Query` object are legacy; they still work, and you will meet them in old code,
but nothing here uses them.

Compare each class with the CREATE TABLE you wrote by hand in Week 13. The
columns are the same columns and the constraints are the same constraints. What
is new is that the class is also a Python object with behaviour, and that a
relationship attribute stands where a join used to be.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, ForeignKey, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """One base per application. It owns the MetaData all tables register in."""


# A many-to-many needs a table with no class of its own: it carries nothing but
# the two foreign keys. This is the "secondary" table, and SQLAlchemy wants it
# as a Core Table rather than a mapped class precisely because it is not an
# entity — it has no identity worth talking about.
book_tags = Table(
    "book_tags",
    Base.metadata,
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)

    loans: Mapped[list[Loan]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="ck_member_name"),)

    def __repr__(self) -> str:
        return f"Member(id={self.id!r}, name={self.name!r})"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)

    books: Mapped[list[Book]] = relationship(secondary=book_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(Text)
    copies: Mapped[int] = mapped_column(default=1)

    loans: Mapped[list[Loan]] = relationship(back_populates="book")
    tags: Mapped[list[Tag]] = relationship(secondary=book_tags, back_populates="books")

    __table_args__ = (CheckConstraint("copies >= 0", name="ck_book_copies"),)

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r})"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    borrowed_on: Mapped[str] = mapped_column(Text)
    due_on: Mapped[str] = mapped_column(Text)
    returned: Mapped[bool] = mapped_column(default=False)

    book: Mapped[Book] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")

    __table_args__ = (
        CheckConstraint("due_on >= borrowed_on", name="ck_loan_dates"),
    )

    def __repr__(self) -> str:
        return f"Loan(id={self.id!r}, book_id={self.book_id!r}, returned={self.returned!r})"
