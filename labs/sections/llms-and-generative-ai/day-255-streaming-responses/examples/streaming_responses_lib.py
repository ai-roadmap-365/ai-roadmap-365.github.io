import time
from typing import Generator, Dict, Any, List

class StreamingTokenAggregator:
    def __init__(self):
        self.accumulated_text = ""
        self.token_count = 0
        self.start_time = 0.0
        self.ttft = 0.0
        self.end_time = 0.0

    def start(self):
        self.start_time = time.time()

    def process_chunk(self, delta_text: str):
        if self.token_count == 0:
            self.ttft = (time.time() - self.start_time) * 1000
        self.accumulated_text += delta_text
        self.token_count += 1

    def finish(self) -> Dict[str, Any]:
        self.end_time = time.time()
        total_duration = (self.end_time - self.start_time) * 1000
        itl = (total_duration - self.ttft) / max(1, self.token_count - 1)

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
