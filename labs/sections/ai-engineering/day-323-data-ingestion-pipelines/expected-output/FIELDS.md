# What each field in the run summary means

Each run prints one line in this shape:

    run N: scanned=A changed=B embedded=C indexed=D dead_lettered=E cursor=F

| Field | Meaning |
| --- | --- |
| `scanned` | Records with `seq` greater than the committed cursor that this run looked at. Zero means the cursor has not moved since the last run. |
| `changed` | Records whose content hash differed from the stored hash, so their body genuinely changed. A record that fails extraction is never hashed and so is never counted here. |
| `embedded` | Chunks passed to the embedding stage. In production this is the line item you pay for, which is why `changed` gates it. |
| `indexed` | Chunks written to the index. Equal to `embedded` in this lab because every embedded chunk is upserted. |
| `dead_lettered` | Records that failed extraction and were captured with their error so the run could continue. |
| `cursor` | The highest `seq` fully processed. Committed only after the batch is written, which is what makes a crash reprocess rather than lose work. |

The final two lines report the index size and the dead-letter contents:

    index: 7 chunks across 4 documents
    dead letters: 1 (doc-3: ExtractionError)

Four documents rather than five because `doc-3` has no payload and fails
extraction on every attempt.
