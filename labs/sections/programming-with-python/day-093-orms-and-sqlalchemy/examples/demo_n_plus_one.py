"""demo_n_plus_one.py — the ORM's most expensive habit, counted and then fixed.

Run it:  python3 examples/demo_n_plus_one.py

The N+1 problem is not a bug in SQLAlchemy. It is the direct consequence of a
relationship attribute being a query in disguise: `member.loans` looks like a
list, so people loop over members and touch it, and each touch is a round trip.
Nothing in the Python source hints at the cost, which is why you count.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, joinedload, selectinload

from counting import QueryCounter
from library import build_engine
from models import Book, Loan, Member, Tag


def rule(label: str) -> None:
    print()
    print(label)
    print("-" * len(label))


def main() -> None:
    engine = build_engine()

    rule("1. The innocent-looking loop")
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            members = session.scalars(select(Member).order_by(Member.id)).all()
            total = sum(len(member.loans) for member in members)
    print(f"members: {len(members)}   loans reached: {total}")
    print(f"statements emitted: {len(counted)}")
    print(counted.report())
    print(f"  That is 1 + {len(members)}. The 1 is the members query; the {len(members)} are")
    print("  one lazy load per member, issued the first time .loans is touched.")
    n_plus_one = len(counted)

    rule("2. Fixed with selectinload — two statements, always")
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            members = session.scalars(
                select(Member).options(selectinload(Member.loans)).order_by(Member.id)
            ).all()
            total = sum(len(member.loans) for member in members)
    print(f"members: {len(members)}   loans reached: {total}")
    print(f"statements emitted: {len(counted)}")
    print(counted.report())
    selectin_count = len(counted)

    rule("3. Fixed with joinedload — one statement")
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            members = session.scalars(
                select(Member).options(joinedload(Member.loans)).order_by(Member.id)
            ).unique().all()
            total = sum(len(member.loans) for member in members)
    print(f"members: {len(members)}   loans reached: {total}")
    print(f"statements emitted: {len(counted)}")
    print(counted.report())
    joined_count = len(counted)

    rule("4. The scoreboard")
    print(f"    lazy (default)   {n_plus_one:>2} statements   <- 1 + N")
    print(f"    selectinload     {selectin_count:>2} statements   <- 1 + 1, whatever N is")
    print(f"    joinedload       {joined_count:>2} statement    <- 1, but wider rows")

    rule("5. Why joinedload is not simply the winner")
    statement = select(Member).options(joinedload(Member.loans)).order_by(Member.id)
    with Session(engine) as session:
        try:
            session.scalars(statement).all()
        except InvalidRequestError as error:
            print("forgetting .unique() raises, and the message says why:")
            print(f"    {str(error).splitlines()[0]}")
        raw_rows = session.connection().exec_driver_sql(
            str(statement.compile(engine))
        ).fetchall()
        distinct = session.scalars(statement).unique().all()
    print(f"rows the JOIN actually returned : {len(raw_rows)}")
    print(f"distinct Member objects built   : {len(distinct)}")
    print("  Every member's columns are repeated once per loan. With a wide parent")
    print("  row and a large collection that duplication is the cost, and it is paid")
    print("  in bytes over the wire. `.unique()` is mandatory on a joinedload of a")
    print("  collection precisely because the driver really does return those rows.")
    print()
    print("  selectinload sends a second SELECT with an IN clause instead: no")
    print("  duplication, no join, but one extra round trip. Choose joinedload for")
    print("  many-to-one and small collections; selectinload for one-to-many.")

    rule("6. It compounds — two levels of laziness")
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            loans = session.scalars(select(Loan).order_by(Loan.id)).all()
            titles = {loan.book.title for loan in loans}
    print(f"loans: {len(loans)}   distinct titles: {len(titles)}")
    print(f"statements emitted: {len(counted)}")
    print("  Not 1 + 24, because the identity map answers the second request for a")
    print("  book already loaded. The count is 1 + the number of DISTINCT books.")

    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            loans = session.scalars(
                select(Loan).options(joinedload(Loan.book)).order_by(Loan.id)
            ).all()
            titles = {loan.book.title for loan in loans}
    print(f"with joinedload(Loan.book): {len(counted)} statement, {len(titles)} titles")
    print("  This is the many-to-one case, and joinedload is the right tool for it:")
    print("  no row multiplication, because each loan has exactly one book.")

    rule("7. A many-to-many, which is where the count really bites")
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            books = session.scalars(select(Book).order_by(Book.id)).all()
            pairs = sum(len(book.tags) for book in books)
    lazy_many = len(counted)
    with Session(engine) as session:
        with QueryCounter(engine) as counted:
            books = session.scalars(
                select(Book).options(selectinload(Book.tags)).order_by(Book.id)
            ).all()
            pairs = sum(len(book.tags) for book in books)
    print(f"books: {len(books)}   book-tag pairs: {pairs}")
    print(f"    lazy         {lazy_many} statements")
    print(f"    selectinload {len(counted)} statements")
    print(counted.report())

    engine.dispose()


if __name__ == "__main__":
    main()
