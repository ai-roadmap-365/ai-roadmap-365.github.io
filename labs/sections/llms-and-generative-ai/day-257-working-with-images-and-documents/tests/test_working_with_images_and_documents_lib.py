import pytest
from examples.working_with_images_and_documents_lib import (
    MultimodalDocumentAnalyzer
)

def test_payload_construction():
    analyzer = MultimodalDocumentAnalyzer()
    payload = analyzer.build_image_payload("b64mockdata", "image/png", "Extract text")

    assert payload["role"] == "user"
    assert len(payload["content"]) == 2
    assert payload["content"][0]["type"] == "image"
    assert payload["content"][0]["source"]["media_type"] == "image/png"
    assert payload["content"][1]["text"] == "Extract text"

def test_unsupported_media_type():
    analyzer = MultimodalDocumentAnalyzer()
    with pytest.raises(ValueError):
        analyzer.build_image_payload("b64mockdata", "image/bmp", "Extract text")

def test_vision_token_calculations():
    analyzer = MultimodalDocumentAnalyzer()
    # Low detail
    assert analyzer.calculate_vision_tokens(2000, 2000, "low") == 85
    # High detail 1024x1024 = 2x2 = 4 tiles -> 4 * 170 + 85 = 765
    assert analyzer.calculate_vision_tokens(1024, 1024, "high") == 765
    # High detail 1920x1080 -> tiles_x=4, tiles_y=3 -> 12 tiles -> 12 * 170 + 85 = 2125
    assert analyzer.calculate_vision_tokens(512, 512, "high") == 255
