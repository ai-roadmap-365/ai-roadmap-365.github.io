"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
from typing import List, Dict, Any, Optional

class ChatStreamFrontendEngine:

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.is_streaming = False
        self.is_scrolled_to_bottom = True
        self.aborted = False

    def submit_user_message(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement submit_user_message.')

    def append_stream_token(self, token: str) -> Optional[str]:
        raise NotImplementedError('TASK 2: implement append_stream_token.')

    def set_viewport_scroll(self, distance_from_bottom_px: float) -> str:
        raise NotImplementedError('TASK 3: implement set_viewport_scroll.')

    def abort_stream(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement abort_stream.')

    def complete_stream(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement complete_stream.')
if __name__ == '__main__':
    engine = ChatStreamFrontendEngine()
    engine.submit_user_message('Hello')
    engine.append_stream_token('Hi!')
    print('Done:', engine.complete_stream())
