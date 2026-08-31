"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Tuple

class ModelSupplyChainScanner:

    def __init__(self, allowed_extensions: Tuple[str, ...]=('.safetensors', '.json', '.txt')):
        self.allowed_extensions = allowed_extensions

    def calculate_sha256(self, file_path: str) -> str:
        raise NotImplementedError('TASK 1: implement calculate_sha256.')

    def scan_model_directory(self, dir_path: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        raise NotImplementedError('TASK 2: implement scan_model_directory.')
if __name__ == '__main__':
    s = ModelSupplyChainScanner()
    print('Scanner ready.')
