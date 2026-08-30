import base64
import math
from typing import Dict, Any, List

class MultimodalDocumentAnalyzer:
    def __init__(self):
        self.supported_image_types = ["image/jpeg", "image/png", "image/webp"]
        self.supported_doc_types = ["application/pdf"]

    def build_image_payload(self, base64_data: str, media_type: str, prompt: str) -> Dict[str, Any]:
        if media_type not in self.supported_image_types:
            raise ValueError(f"Unsupported image media type: {media_type}")
        return {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_data
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }

    def calculate_vision_tokens(self, width: int, height: int, detail: str = "high") -> int:
        if detail == "low":
            return 85
        tiles_x = math.ceil(min(width, 2048) / 512)
        tiles_y = math.ceil(min(height, 2048) / 512)
        total_tiles = tiles_x * tiles_y
        return (total_tiles * 170) + 85

def run_multimodal_demo():
    analyzer = MultimodalDocumentAnalyzer()
    payload = analyzer.build_image_payload("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=", "image/png", "Extract invoice.")
    tokens = analyzer.calculate_vision_tokens(1024, 1024, "high")
    print(f"Multimodal Demo Executed. Tokens: {tokens}")
    return payload, tokens

if __name__ == "__main__":
    run_multimodal_demo()
