# The brief — Fenwick Road Community Library

This is the document you were handed. It is written the way requirements
actually arrive: in prose, by somebody who knows the library and not the
database. Read it twice before you write a single `CREATE TABLE`.

Everything below about the library, its members and its loans is **invented for
this exercise**. The books and their authors are real published works; the
people, email addresses, dates, fines and reservations are not, and no real
borrowing record was used anywhere in this lab.

---

## What the library does

> We lend books. We own a few thousand titles, though for now we only need the
> handful we have catalogued so far.
>
> Every book has a title and, usually, a thirteen-digit ISBN — except the very
> old ones, which were printed before ISBNs existed. We would like to record
> what we paid for each book, because the trustees ask about it, and we would
> like to know roughly when it was published.
>
> Books are shelved by category, and the categories nest: Fiction contains
> Science Fiction, which contains Cyberpunk. We add and rename categories
> fairly often, and we sometimes move a whole branch under a different parent.
>
> Some books have more than one author. *The C Programming Language* has two,
> and the one everybody calls SICP has three. The order matters — the cover
> credits them in a particular order and so should we.
>
> When a book falls apart or goes missing we *withdraw* it. It leaves the
> shelves, but we must still be able to see it in old loan records, so please
> do not simply delete it.
>
> Members join, give us an email address we use to contact them, and are on one
> of three membership tiers: standard, student, or staff. Members also leave.
> When they do we stop counting them as members, but their loan history and any
> money they still owe us has to survive.
>
> A loan records that a member took a book out on a particular date, that it is
> due back on a particular date, and — once it comes back — the date it came
> back. If it comes back late we charge a fine, in pounds and pence.
>
> If a book is out on loan, a member can reserve it. Several members can be
> waiting for the same book, and they are served in the order they asked. A
> reservation can also be cancelled, expire, or be collected.
>
> We are a small charity with volunteers on the desk, so it must be difficult
> to record something impossible: a loan due before it was borrowed, a negative
> fine, a membership tier nobody has heard of, or a reservation against a book
> we do not own.

---

## The ten questions the library asks

Your schema exists to answer these. If a question is awkward to answer, that is
information about the schema, not about the question.

1. How many books are on the shelves right now, and how many of them are out on
   loan?
2. Which current members have never borrowed anything?
3. Which books have more than one author, and who are they in credited order?
4. Which loans are overdue as of the report time, and by how many whole days?
5. How much does each member owe us in fines, in pounds — including members who
   have since left?
6. Who are the two most active borrowers in each membership tier, counting only
   current members, and including someone who has borrowed nothing if that is
   what the tier looks like?
7. For every book with people waiting, what is the reservation queue, in order?
8. How many loans did we start each month, and what is the running total across
   the year so far?
9. What sits underneath the Fiction category, at any depth, and how many books
   are in each of those categories?
10. Which authors have never had any of their books borrowed?

---

## Reporting time

Every "as of now" question in this lab is answered as of a fixed instant:

```text
2026-08-16T09:00:00Z
```

That is deliberate. A report whose answer depends on when you happen to run it
cannot be tested, and cannot be compared against a colleague's. The report
script takes the instant as a parameter with that value as its default.

---

## What to do

1. Read `01_schema.sql` and write the schema. The numbered comments say what
   each table must hold and which decision you are being asked to make.
2. Run `bash 03_check.sh` — it will tell you which of the ten questions your
   schema and queries currently answer correctly.
3. Write the queries in `02_questions.sql`, one per question.
4. When `03_check.sh` reports `10 of 10`, compare your schema with
   `../examples/01_schema.sql` and read the reasoning in the lesson.

Do not read the examples directory first. The comparison is worth far more
after you have made your own choices and found out which of them hurt.
