import time
from typing import Generator, Dict, Any, List

# perf_counter, not time(): time() is a wall clock that an NTP correction can
# step backwards, which would report a negative latency. perf_counter is
# monotonic and is the right clock for measuring an interval.

class StreamingTokenAggregator:
    def __init__(self):
        # TODO: Initialize tracking attributes
        pass

    def start(self):
        # TODO: Record start time
        pass

    def process_chunk(self, delta_text: str):
        # TODO: Record TTFT and accumulate text
        pass

    def finish(self) -> Dict[str, Any]:
        # TODO: Calculate ITL and return summary
        pass

def simulate_mock_stream() -> Generator[str, None, None]:
    # TODO: Yield mock token chunks
    pass
