#!/usr/bin/env python3
"""The script we are starting from. Everything it says, it says with print().

Run it:

    python3 examples/01_prints.py

Then read the output and ask the four questions that matter once this script
is running somewhere you are not:

    1. WHEN did each line happen? There is no timestamp. If two of these
       lines are three hours apart you cannot tell.
    2. WHICH RUN is this? If it runs hourly, yesterday's output and today's
       are identical text in the same file with nothing to separate them.
    3. HOW BAD is each line? "skipping record" and "could not write the
       output" are the same shape of text. `grep` cannot tell them apart, so
       neither can an alert.
    4. HOW DO I TURN IT DOWN? You edit the file, and you deploy. There is no
       other way, because the decision to print is baked into every call.

And one more, which is the one that gets people fired: line 3 of the output
prints the API key. It is now in the terminal scrollback, in the CI job log,
and in whatever file the output was redirected to.

Nothing here is a straw man. This is what a working script looks like before
anybody has needed to operate it.
"""

# A tiny data-preparation job. Six records in, some of them bad.
RECORDS = [
    {"id": 1, "text": "the cat sat on the mat", "label": "neutral"},
    {"id": 2, "text": "", "label": "neutral"},
    {"id": 3, "text": "shipping was late and the box was crushed", "label": "negative"},
    {"id": 4, "text": "arrived early, works perfectly", "label": "positive"},
    {"id": 5, "text": "no opinion", "label": "unknown"},
    {"id": 6, "text": "great value for the price", "label": "positive"},
]

VALID_LABELS = {"neutral", "negative", "positive"}
API_KEY = "sk-live-9f2c4a7b1e63"  # invented for this lab; not a real credential


def prepare(records):
    print("starting preparation")
    print("using API key " + API_KEY)  # never do this. It is done here on purpose.
    kept = []
    for record in records:
        print("processing record " + str(record["id"]))
        if not record["text"]:
            print("skipping record " + str(record["id"]) + ": empty text")
            continue
        if record["label"] not in VALID_LABELS:
            print("skipping record " + str(record["id"]) + ": unknown label")
            continue
        kept.append(record)
    print("kept " + str(len(kept)) + " of " + str(len(records)) + " records")
    return kept


def main():
    kept = prepare(RECORDS)
    # The actual RESULT of the program, mixed into the same stream as all the
    # commentary above. A caller that wants to pipe the result somewhere gets
    # the commentary too.
    for record in kept:
        print(f"{record['id']}\t{record['label']}\t{record['text']}")
    print("done")


if __name__ == "__main__":
    main()
