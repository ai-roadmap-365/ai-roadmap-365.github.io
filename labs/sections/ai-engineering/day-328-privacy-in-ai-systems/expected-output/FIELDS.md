# Reading the privacy output

## The redaction block

    From: [email:c4e2790ada]
    findings: card=1 email=1 ip=1 national_id=1 phone=1

Each token is `[category:digest]`, where the digest is the first ten hex characters of a salted SHA-256 of the original value.

| Property | Why it matters |
| --- | --- |
| **Stable** | The same value always yields the same token, so one person stays followable across records for debugging without their identity being visible. |
| **Salted** | Without a salt, a hash of a short value is reversed by enumeration — there are only so many phone numbers. |
| **Non-reversible** | The token is not the identifier wearing a hat. |

`pseudonym stable across records: True` confirms the first property across two separate redaction calls.

## The data flow

    subject-42 present in: ['audit_log', 'database', 'response_cache', 'vector_index']

Four stores hold data for one subject. This list is what an erasure runs against — otherwise it runs against whatever someone remembers.

## The two erasure runs

    INCOMPLETE deleted_from=2 still_present=audit_log,response_cache
    COMPLETE   deleted_from=2 still_present=none

| Field | Meaning |
| --- | --- |
| status | `COMPLETE` only when a read-back finds the subject in no store. |
| `deleted_from` | Stores that actually held the subject and no longer do. |
| `still_present` | Stores that hold them after the deletes ran. The whole point of the control. |

The first run is the realistic failure: someone deletes from the database and the vector index — the two stores that come to mind — and misses the cache and the audit log. Reporting from the delete calls alone would have called that a success.

## Minimisation

    kept: {'tier': 'pro'}

Three fields collected, one retained. Data never kept cannot leak and does not need deleting.
