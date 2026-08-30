import re
from collections import defaultdict
from typing import List, Dict, Tuple, Any

def regex_pre_tokenize(text: str) -> List[str]:
    pattern = r"'\w+|\w+|[^\w\s]"
    return re.findall(pattern, text)

class BPETokenizer:
    def __init__(self, num_merges: int = 10):
        self.num_merges = num_merges
        self.merges: List[Tuple[str, str]] = []
        self.vocab: Dict[str, int] = {
            "<pad>": 0,
            "<unk>": 1,
            "<bos>": 2,
            "<eos>": 3
        }
        self.inverse_vocab: Dict[int, str] = {v: k for k, v in self.vocab.items()}

    def _get_stats(self, vocab: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, str], int]:
        pairs = defaultdict(int)
        for word_tuple, freq in vocab.items():
            for i in range(len(word_tuple) - 1):
                pair = (word_tuple[i], word_tuple[i+1])
                pairs[pair] += freq
        return pairs

    def _merge_vocab(self, pair: Tuple[str, str], vocab: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, ...], int]:
        new_vocab = {}
        bigram = " ".join(pair)
        replacement = "".join(pair)
        for word_tuple, freq in vocab.items():
            w_str = " ".join(word_tuple)
            w_new = w_str.replace(bigram, replacement)
            new_vocab[tuple(w_new.split())] = freq
        return new_vocab

    def train(self, corpus: List[str]):
        word_freqs = defaultdict(int)
        for text in corpus:
            for word in regex_pre_tokenize(text):
                chars = tuple(list(word) + ["</w>"])
                word_freqs[chars] += 1

        current_vocab = word_freqs
        for _ in range(self.num_merges):
            pairs = self._get_stats(current_vocab)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)
            self.merges.append(best_pair)
            current_vocab = self._merge_vocab(best_pair, current_vocab)

        # Build vocabulary
        for word_tuple in current_vocab.keys():
            for subword in word_tuple:
                if subword not in self.vocab:
                    idx = len(self.vocab)
                    self.vocab[subword] = idx
                    self.inverse_vocab[idx] = subword

    def encode_word(self, word: str) -> List[str]:
        tokens = list(word) + ["</w>"]
        for pair in self.merges:
            i = 0
            new_tokens = []
            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
                    new_tokens.append(pair[0] + pair[1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        return tokens

    def encode(self, text: str) -> List[int]:
        words = regex_pre_tokenize(text)
        token_ids = []
        for word in words:
            subwords = self.encode_word(word)
            for sw in subwords:
                token_ids.append(self.vocab.get(sw, self.vocab["<unk>"]))
        return token_ids

def pad_and_mask_batch(batch_ids: List[List[int]], pad_idx: int = 0) -> Tuple[List[List[int]], List[List[int]]]:
    max_len = max(len(seq) for seq in batch_ids)
    padded = []
    masks = []
    for seq in batch_ids:
        pad_len = max_len - len(seq)
        padded.append(seq + [pad_idx] * pad_len)
        masks.append([1] * len(seq) + [0] * pad_len)
    return padded, masks

def run_tokenization_demo():
    corpus = [
        "low lower lowest",
        "new newer newest",
        "wide wider widest"
    ]
    tok = BPETokenizer(num_merges=5)
    tok.train(corpus)
    encoded = tok.encode("lowest newest")
    padded, masks = pad_and_mask_batch([[1, 2, 3], [4, 5]], pad_idx=0)
    print(f"Tokenization Demo: Vocab Size = {len(tok.vocab)}, Merges = {len(tok.merges)}, Padded Len = {len(padded[0])}")
    return tok, encoded, padded, masks

if __name__ == "__main__":
    run_tokenization_demo()
