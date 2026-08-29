# The domain: Northside Gym membership

This is the page of plain-English rules a gym owner gave you. Everything you
model must come from these sentences — and nothing you model should come from
anywhere else. Read them twice before you write a line of code.

## The rules, as the owner stated them

1. The club is called **Northside Gym**. It keeps a list of its members.
2. Every **member** has a **membership number**, a name, and the date they
   joined. The membership number is written `GYM-` followed by exactly four
   digits, for example `GYM-0007`. No two members ever share a number, and a
   member's number never changes for as long as they are a member.
3. Two members with the same name are still two different people. Two records
   with the same membership number are the same member.
4. Every member is on exactly one **plan** at a time. A plan has a **tier** —
   either **basic** or **plus** — and a **monthly price**.
5. A **price** is an amount of money in a currency. All of Northside Gym's
   prices are in euros (`EUR`). A price is never negative, and you can never
   add a euro amount to a dollar amount.
6. A member on the **basic** tier may **check in** at most **12 times in any
   one calendar month**. A member on the **plus** tier may check in as often
   as they like.
7. A **check-in** records which member came in and on which day. A check-in,
   once it has happened, never changes.
8. A member may **switch plans** at any time. Switching does not erase the
   check-ins they already have.
9. A **billing period** is a start date and an end date. The start date must
   be on or before the end date.
10. The club's **monthly revenue** is the sum of the monthly prices of every
    member's current plan. It is one money amount, in one currency.
11. Anything the rules forbid — an unknown membership number, a duplicate
    enrolment, a thirteenth basic check-in in a month, a negative price,
    adding two currencies — must be **refused with a clear error**, not
    silently allowed or silently ignored.

## Vocabulary the owner uses

These are the words that must appear in your code, spelled the way the owner
spells them: *club*, *member*, *membership number*, *plan*, *tier*, *basic*,
*plus*, *price*, *check in*, *switch plan*, *billing period*, *monthly
revenue*. If your code calls a member a "user record" or a plan a "type
string", the owner can no longer read it, and neither will you in six months.

## What is deliberately not here

The rules say nothing about payments, refunds, lockers, classes, trainers, or
a website. Do not model any of them. Building what the rules do not ask for is
the fastest way to make a small model unmaintainable.
