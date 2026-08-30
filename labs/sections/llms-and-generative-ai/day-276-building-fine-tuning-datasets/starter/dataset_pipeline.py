# Starter: Dataset Processing Pipeline
from typing import Dict, List, Any, Tuple

class DatasetPipeline:
    def __init__(self, pad_token_id: int = 0, ignore_index: int = -100):
        self.pad_token_id = pad_token_id
        self.ignore_index = ignore_index

    def convert_alpaca_to_chatml(self, alpaca_item: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
        return {"messages": []}

    def decontaminate_samples(
        self,
        train_samples: List[Dict[str, Any]],
        eval_queries: List[str],
        n_gram_size: int = 5
    ) -> Tuple[List[Dict[str, Any]], int]:
        return train_samples, 0

    def generate_loss_masked_labels(
        self,
        chatml_sample: Dict[str, List[Dict[str, str]]],
        mock_vocab: Dict[str, int]
    ) -> Dict[str, List[int]]:
        return {"input_ids": [], "labels": []}
