"""Day 092 — the one domain, in the one place.

Every example in this lab models the SAME four books. Keeping the data in a
single module is what makes the comparison honest: when the key-value shape and
the document shape disagree about what a query returns, the difference is the
shape, not the data.

The books and their authors are real and checkable. Nothing about a real
person's borrowing history appears anywhere in this lab.

Notice one thing about the shape below before you go on. `authors` is a LIST.
Relationally that list cannot live on the book row at all — a column holds one
value — which is exactly why Week 13 gave books and authors a junction table.
Here it is simply a field. That is the document model's whole pitch, and the
rest of the lab is about what it costs.
"""

BOOKS = [
    {
        "book_id": 101,
        "title": "The C Programming Language",
        "published_year": 1978,
        "shelf": "A3",
        "authors": ["Brian W. Kernighan", "Dennis M. Ritchie"],
    },
    {
        "book_id": 102,
        "title": "The Mythical Man-Month",
        "published_year": 1975,
        "shelf": "B1",
        "authors": ["Frederick P. Brooks Jr."],
    },
    {
        "book_id": 103,
        "title": "Artificial Intelligence: A Modern Approach",
        "published_year": 1995,
        "shelf": "C2",
        "authors": ["Stuart J. Russell", "Peter Norvig"],
    },
    {
        "book_id": 104,
        "title": "The Practice of Programming",
        "published_year": 1999,
        "shelf": "A3",
        "authors": ["Brian W. Kernighan", "Rob Pike"],
    },
]

# The document that is wrong in one character. Its field is "titel", not
# "title". Three of the four shapes in this lab accept it without complaint.
MISSPELLED_BOOK = {
    "book_id": 105,
    "titel": "Compilers: Principles, Techniques, and Tools",
    "published_year": 1986,
    "shelf": "C1",
    "authors": ["Alfred V. Aho", "Ravi Sethi", "Jeffrey D. Ullman"],
}


def key_for(book_id: int) -> str:
    """The key-value convention used throughout: a type prefix and an id."""
    return f"book:{book_id}"
