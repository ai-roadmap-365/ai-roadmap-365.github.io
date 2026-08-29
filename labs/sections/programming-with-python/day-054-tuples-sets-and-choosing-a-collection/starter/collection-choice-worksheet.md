# Collection-choice worksheet — Day 054

Choosing the right collection is a design decision you make *before* you code.
For each scenario below, pick ONE of `list`, `tuple`, `set`, or `dict`, and
justify it against the four questions that decide the answer:

1. **Mutable?** Will the data change after you build it?
2. **Ordered / indexed?** Do you need to keep insertion order or reach an item
   by position?
3. **Unique?** Must duplicates be removed automatically?
4. **Fast lookup by key?** Do you need to check membership or fetch a value in
   roughly one step regardless of size?

Fill in a choice and a one-sentence reason for each. There is a model answer
for every row in the instructor solution — try it yourself first.

## Scenarios

| # | Scenario | Your choice | Why (one sentence) |
|---|----------|-------------|--------------------|
| 1 | The (latitude, longitude) of a city, passed around and never changed | | |
| 2 | A growing to-do list the user adds items to and reorders | | |
| 3 | The set of stop-words to strip from text before feeding it to a model | | |
| 4 | A phone book mapping each name to a phone number | | |
| 5 | The unique words (vocabulary) seen while scanning a large document | | |
| 6 | The RGB colour of a pixel, used as a key to count how often it appears | | |
| 7 | An ordered playlist where the same song may appear twice | | |
| 8 | Deduplicating a million scraped URLs, then testing "have I seen this one?" | | |

## Reflection (answer after building the program)

1. Which single property most often decided your answer above — mutability,
   order, uniqueness, or lookup speed? Give an example.

   > 

2. Scenario 6 uses a colour as a **dictionary key**. Why must that key be a
   tuple, not a list? (Hint: hashable.)

   > 

3. In the program you built, `compare()` returns a `SetReport` — an immutable
   tuple record. Name one bug that immutability prevents a caller from causing.

   > 
