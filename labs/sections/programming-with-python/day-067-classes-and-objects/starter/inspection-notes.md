# Exercise 6 — inspect the machinery and write down what you see

A class is not magic. It is an object that holds functions; an instance is
an object that holds its own attribute dictionary; and attribute lookup
checks the instance first, then the class. This exercise makes you *look* at
that instead of taking it on faith.

Run the reference inspector first, from the lab directory:

```bash
python3 examples/machinery.py
```

Then run each command below against **your own** class and fill in the
"What I saw" column with the literal output. Every command is one line; copy
it whole.

## 6.1 — Two instances are two different objects

```bash
python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; a = Account('ada', 100); b = Account('bob', 100); print(type(a).__name__, a is b, id(a) == id(b), type(a) is type(b))"
```

| Question | What I saw |
| --- | --- |
| What does `type(a).__name__` print? | _fill in_ |
| Is `a is b` true or false, and why? | _fill in_ |
| Is `type(a) is type(b)` true, and what does that tell you? | _fill in_ |

## 6.2 — State lives on the instance

```bash
python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; a = Account('ada', 100); b = Account('bob', 100); a.deposit(50); print(vars(a)); print(vars(b))"
```

| Question | What I saw |
| --- | --- |
| Which keys are in `vars(a)`? | _fill in_ |
| Do the two instances hold different values for the same keys? | _fill in_ |
| Is `deposit` one of the keys? Where does it live instead? | _fill in_ |

## 6.3 — Behaviour lives on the class

```bash
python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; print(sorted(n for n in vars(Account) if not n.startswith('__')))"
```

| Question | What I saw |
| --- | --- |
| Which names does the class dictionary hold? | _fill in_ |
| Which of them are functions, and which are plain values? | _fill in_ |
| `Account.currency` is not in `vars(a)` — so how does `a.currency` work? | _fill in_ |

## 6.4 — A method call is a function call with `self` supplied

```bash
python3 -c "import sys; sys.path.insert(0, 'starter'); from account import Account; a = Account('ada', 100); print(type(Account.deposit).__name__, type(a.deposit).__name__, a.deposit.__self__ is a, a.deposit.__func__ is Account.deposit)"
```

| Question | What I saw |
| --- | --- |
| What is `type(Account.deposit)`? What is `type(a.deposit)`? | _fill in_ |
| What is `a.deposit.__self__`? | _fill in_ |
| Write out what `a.deposit(50)` becomes in unsugared form. | _fill in_ |

## 6.5 — Write it in your own words

Answer in two or three sentences each, from what you saw above:

1. Where does an instance's state live, and where does its behaviour live?
2. What exactly does `self` refer to, and who passes it?
3. Why did the class version refuse `a.balance = -500` when the dict
   version happily accepted `account["balance"] = -500`?
4. Name one thing in this lab that convinced you a class is "a dict of
   state plus a dict of functions, with syntax on top."
