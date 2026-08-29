# Weather CLI worksheet — Day 028

Run your completed `weather.sh` and record what it returns. Values change with
the weather and the day — that is expected.

## 1. Pick a location

- Place name: `____________`
- Latitude: `______`   Longitude: `______`
  (Search "<place> latitude longitude" if you don't know them.)

## 2. Current conditions (network on)

Command: `bash starter/weather.sh <LAT> <LON>`

- Time reported: `____________`
- Temperature: `______ °C`
- Wind: `______ km/h`

## 3. What the script prints when the network is down

Turn off your network (or point the client at a deliberately unreachable URL),
then run the command again and paste the exact output:

```text
____________________________________________________
____________________________________________________
```

- Did the script crash, or fail with a clear message? `____________`
- What exit code did it return? (`echo $?` right after) `______`

## 4. Trace the pipeline (2–3 sentences)

For your successful run in section 2, say which of the six pipeline stages
produced each line of output — the `curl` fetch, the parse, or the
presentation:

> _your answer here_
