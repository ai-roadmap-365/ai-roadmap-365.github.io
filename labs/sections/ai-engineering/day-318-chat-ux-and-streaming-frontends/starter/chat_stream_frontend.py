import time
from typing import List, Dict, Any, Optional

class ChatStreamFrontendEngine:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.is_streaming = False
        self.is_scrolled_to_bottom = True
        self.aborted = False
        
    def submit_user_message(self, text: str) -> Dict[str, Any]:
        user_msg = {
            "id": f"msg_user_{len(self.messages)+1}",
            "role": "user",
            "content": text.strip(),
            "timestamp": time.time(),
            "status": "sent"
        }
        self.messages.append(user_msg)
        self.is_streaming = True
        self.aborted = False
        
        asst_msg = {
            "id": f"msg_asst_{len(self.messages)+1}",
            "role": "assistant",
            "content": "",
            "timestamp": time.time(),
            "status": "streaming"
        }
        self.messages.append(asst_msg)
        return asst_msg

    def append_stream_token(self, token: str) -> Optional[str]:
        if not self.is_streaming or self.aborted:
            return None
            
        asst_msg = self.messages[-1]
        asst_msg["content"] += str(token)
        return asst_msg["content"]

    def set_viewport_scroll(self, distance_from_bottom_px: float) -> str:
        if float(distance_from_bottom_px) <= 50.0:
            self.is_scrolled_to_bottom = True
            return "AUTO_SCROLL_STICK"
        else:
            self.is_scrolled_to_bottom = False
            return "AUTO_SCROLL_LOCKED"

    def abort_stream(self) -> Dict[str, Any]:
        self.aborted = True
        self.is_streaming = False
        if self.messages and self.messages[-1]["role"] == "assistant":
            self.messages[-1]["status"] = "aborted"
        return {"status": "ABORTED", "partial_content": self.messages[-1]["content"]}

    def complete_stream(self) -> Dict[str, Any]:
        self.is_streaming = False
        if self.messages and self.messages[-1]["role"] == "assistant":
            self.messages[-1]["status"] = "completed"
        return {"status": "COMPLETED", "final_content": self.messages[-1]["content"]}

if __name__ == "__main__":
    engine = ChatStreamFrontendEngine()
    engine.submit_user_message("Hello")
    engine.append_stream_token("Hi!")
    print("Done:", engine.complete_stream())
