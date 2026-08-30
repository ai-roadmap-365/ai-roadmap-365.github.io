import time
from typing import Generator, Dict, Any, List

# perf_counter, not time(): time() is a wall clock that an NTP correction can
# step backwards, which would report a negative latency. perf_counter is
# monotonic and is the right clock for measuring an interval.

class StreamingTokenAggregator:
    def __init__(self):
        self.accumulated_text = ""
        self.token_count = 0
        self.start_time = 0.0
        self.ttft = 0.0
        self.end_time = 0.0

    def start(self):
        self.start_time = time.perf_counter()

    def process_chunk(self, delta_text: str):
        if self.token_count == 0:
            self.ttft = (time.perf_counter() - self.start_time) * 1000
        self.accumulated_text += delta_text
        self.token_count += 1

    def finish(self) -> Dict[str, Any]:
        self.end_time = time.perf_counter()
        total_duration = (self.end_time - self.start_time) * 1000
        # Inter-token latency is the gap BETWEEN tokens, so a stream of one
        # token has none. Dividing by max(1, n-1) there would report the whole
        # tail of the request as if it were a gap.
        gaps = self.token_count - 1
        itl = (total_duration - self.ttft) / gaps if gaps > 0 else 0.0

        return {
            "text": self.accumulated_text,
            "token_count": self.token_count,
            "ttft_ms": round(self.ttft, 2),
            "itl_ms": round(itl, 2),
            "total_duration_ms": round(total_duration, 2)
        }

def simulate_mock_stream() -> Generator[str, None, None]:
    words = ["Real-time", " streaming", " slashes", " perceived", " latency", " drastically."]
    for word in words:
        time.sleep(0.01)
        yield word

def run_streaming_demo():
    aggregator = StreamingTokenAggregator()
    aggregator.start()
    for chunk in simulate_mock_stream():
        aggregator.process_chunk(chunk)
    result = aggregator.finish()
    print("Streaming Demo Executed. Text:", result["text"])
    return result

if __name__ == "__main__":
    run_streaming_demo()
