# Fine-Tuning Dataset Processing & Validation Pipeline
import re
from typing import Dict, List, Any, Set, Tuple

class DatasetPipeline:
    """End-to-end dataset transformation, decontamination, and loss-masking engine."""

    def __init__(self, pad_token_id: int = 0, ignore_index: int = -100):
        self.pad_token_id = pad_token_id
        self.ignore_index = ignore_index

    def convert_alpaca_to_chatml(self, alpaca_item: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
        """Converts Alpaca (instruction, input, output) to ChatML format."""
        user_content = alpaca_item["instruction"]
        if alpaca_item.get("input") and alpaca_item["input"].strip():
            user_content += "\n\n" + alpaca_item["input"].strip()
            
        return {
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": alpaca_item["output"]}
            ]
        }

    def convert_sharegpt_to_chatml(self, sharegpt_item: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """Converts ShareGPT conversations list to ChatML format."""
        role_map = {"human": "user", "gpt": "assistant", "system": "system"}
        messages = []
        for msg in sharegpt_item["conversations"]:
            role = role_map.get(msg["from"], "user")
            messages.append({"role": role, "content": msg["value"]})
        return {"messages": messages}

    def decontaminate_samples(
        self,
        train_samples: List[Dict[str, Any]],
        eval_queries: List[str],
        n_gram_size: int = 5
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Filters out training samples that share n-gram overlaps with eval queries."""
        eval_ngrams: Set[str] = set()
        for q in eval_queries:
            words = self._tokenize_words(q)
            for i in range(len(words) - n_gram_size + 1):
                eval_ngrams.add(" ".join(words[i:i + n_gram_size]))

        clean_samples = []
        filtered_count = 0

        for sample in train_samples:
            text = " ".join([m["content"] for m in sample["messages"]])
            words = self._tokenize_words(text)
            sample_ngrams = {" ".join(words[i:i + n_gram_size]) for i in range(len(words) - n_gram_size + 1)}
            
            if sample_ngrams.intersection(eval_ngrams):
                filtered_count += 1
            else:
                clean_samples.append(sample)

        return clean_samples, filtered_count

    def compute_token_statistics(self, samples: List[Dict[str, Any]]) -> Dict[str, float]:
        """Computes summary statistics on sequence word lengths."""
        lengths = [sum(len(self._tokenize_words(m["content"])) for m in s["messages"]) for s in samples]
        if not lengths:
            return {"count": 0, "mean": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0}

        sorted_lens = sorted(lengths)
        n = len(sorted_lens)
        mean_val = sum(sorted_lens) / n
        median_val = sorted_lens[n // 2]
        p95_val = sorted_lens[int(n * 0.95)] if n > 0 else 0
        max_val = sorted_lens[-1]

        return {
            "count": float(n),
            "mean": float(mean_val),
            "median": float(median_val),
            "p95": float(p95_val),
            "max": float(max_val)
        }

    def generate_loss_masked_labels(
        self,
        chatml_sample: Dict[str, List[Dict[str, str]]],
        mock_vocab: Dict[str, int]
    ) -> Dict[str, List[int]]:
        """Simulates ChatML tokenization and generates -100 loss masks on prompt tokens."""
        input_ids: List[int] = []
        labels: List[int] = []

        for msg in chatml_sample["messages"]:
            role = msg["role"]
            content = msg["content"]
            # Format: <|im_start|>role\\ncontent<|im_end|>
            words = [f"<|im_start|>{role}"] + self._tokenize_words(content) + ["<|im_end|>"]
            tokens = [mock_vocab.get(w, 100) for w in words]
            
            input_ids.extend(tokens)
            if role in ["system", "user"]:
                # Mask prompt tokens with ignore_index (-100)
                labels.extend([self.ignore_index] * len(tokens))
            else:
                # Assistant tokens are trained (loss computed)
                labels.extend(tokens)

        return {
            "input_ids": input_ids,
            "labels": labels
        }

    def _tokenize_words(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())
