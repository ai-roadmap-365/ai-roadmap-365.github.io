"""Going back out: ``model_dump``, ``model_dump_json``, and where the round trip breaks.

Validation is only half a boundary. Data has to leave too, and the assumption
that ``Model.model_validate(instance.model_dump())`` always works is one of the
most common things people get wrong about pydantic — and it is wrong for
ordinary, sensible reasons rather than exotic ones.

This module demonstrates each of them by doing it. Run it directly:

    python3 examples/serialize.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import Reading
from pydantic import TypeAdapter, ValidationError

LAB_DIR = Path(__file__).resolve().parent.parent
BATCH = LAB_DIR / "data" / "raw-readings.json"


def first_valid_record() -> dict[str, Any]:
    with BATCH.open(encoding="utf-8") as handle:
        return json.load(handle)[0]


def _outcome(payload: Any) -> str:
    try:
        Reading.model_validate(payload)
    except ValidationError as exc:
        return "refused: " + ", ".join(
            f"{'.'.join(str(p) for p in e['loc'])} [{e['type']}]" for e in exc.errors()
        )
    return "accepted"


def main() -> int:
    reading = Reading.model_validate(first_valid_record())

    print("1. Two dumps, two different jobs")
    print()
    dumped = reading.model_dump()
    print(f"model_dump()      -> recorded_at is a {type(dumped['recorded_at']).__name__}")
    print(f"model_dump_json() -> {reading.model_dump_json()}")
    print()
    print("model_dump gives Python objects; model_dump_json gives a JSON string and")
    print("has to turn the datetime into text on the way. Reach for the second when")
    print("the destination is a file or a socket, and the first when it is more Python.")
    print()

    print("2. The field name is not the wire name")
    print()
    print(f"default keys  : {list(dumped)}")
    print(f"by_alias=True : {list(reading.model_dump(by_alias=True))}")
    print()
    print("The model reads `pm2_5` on the way in because of the alias, and writes")
    print("`pm25` on the way out unless you ask for by_alias. If the thing at the")
    print("other end is the same vendor system, you almost certainly want by_alias.")
    print()

    print("3. The round trip is not symmetric")
    print()
    print(f"model_validate(model_dump())                  -> {_outcome(dumped)}")
    trimmed = reading.model_dump(by_alias=True, exclude={"band"})
    print(f"model_validate(model_dump(by_alias, -band))   -> {_outcome(trimmed)}")
    print()
    print("`band` is a computed_field. It is serialised because a consumer wants it,")
    print("and it is refused on the way back in because `extra='forbid'` is doing its")
    print("job: nothing computed is an input. Both behaviours are correct; the bug")
    print("would be assuming they compose.")
    print()

    print("4. Trimming the output at the point of use")
    print()
    print(f"exclude={{'operator'}}   -> {list(reading.model_dump(exclude={'operator'}))}")
    print(f"exclude_none=True     -> {list(reading.model_dump(exclude_none=True))}")
    print(f"include={{'reading_id'}} -> {reading.model_dump(include={'reading_id'})}")
    print()
    print("`operator` is a name. It is in the record because the pipeline needs")
    print("provenance, and it is excluded here because the published extract does")
    print("not. Deciding that at the serialiser rather than in six call sites is")
    print("the whole reason these arguments exist.")
    print()

    print("5. TypeAdapter: validation for things that are not models")
    print()
    batch_adapter = TypeAdapter(list[Reading])
    print("TypeAdapter(list[Reading]) validates a whole list in one call")
    good = [first_valid_record()]
    print(f"  one good record  -> {len(batch_adapter.validate_python(good))} Reading object(s)")
    try:
        batch_adapter.validate_python(good + [{"reading_id": "RD-0100"}])
    except ValidationError as exc:
        locs = [tuple(e["loc"]) for e in exc.errors()]
        print(f"  one bad appended -> {len(exc.errors())} errors, loc[0]={locs[0]}")
        print("     note the leading index: loc tells you WHICH element failed")
    print()
    ints = TypeAdapter(list[int])
    print(f"TypeAdapter(list[int]).validate_python(['1', '2']) -> {ints.validate_python(['1', '2'])}")
    print(f"TypeAdapter(list[int]).dump_json([1, 2])           -> {ints.dump_json([1, 2])!r}")
    print()

    print("6. The schema, for free")
    print()
    schema = Reading.model_json_schema()
    print(f"required fields : {sorted(schema['required'])}")
    print(f"pm2_5 property  : {json.dumps(schema['properties']['pm2_5'], sort_keys=True)}")
    print()
    print("That is a JSON Schema document, generated from the annotations. It is")
    print("what FastAPI publishes as OpenAPI, and it is what you hand a language")
    print("model when you want structured output back.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
