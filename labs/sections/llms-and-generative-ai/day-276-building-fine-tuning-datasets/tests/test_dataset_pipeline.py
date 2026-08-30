import pytest
from dataset_pipeline import DatasetPipeline

@pytest.fixture
def pipeline():
    return DatasetPipeline()

def test_alpaca_to_chatml_conversion(pipeline):
    alpaca = {
        "instruction": "Translate to SQL",
        "input": "Find users where age > 30",
        "output": "SELECT * FROM users WHERE age > 30;"
    }
    chatml = pipeline.convert_alpaca_to_chatml(alpaca)
    assert len(chatml["messages"]) == 3
    assert chatml["messages"][0]["role"] == "system"
    assert "Translate to SQL" in chatml["messages"][1]["content"]
    assert "Find users where age > 30" in chatml["messages"][1]["content"]
    assert chatml["messages"][2]["role"] == "assistant"
    assert "SELECT * FROM users" in chatml["messages"][2]["content"]

def test_sharegpt_to_chatml_conversion(pipeline):
    sharegpt = {
        "conversations": [
            {"from": "system", "value": "System init."},
            {"from": "human", "value": "Hello!"},
            {"from": "gpt", "value": "Hi there!"}
        ]
    }
    chatml = pipeline.convert_sharegpt_to_chatml(sharegpt)
    assert len(chatml["messages"]) == 3
    assert chatml["messages"][0]["role"] == "system"
    assert chatml["messages"][1]["role"] == "user"
    assert chatml["messages"][2]["role"] == "assistant"

def test_decontamination_filtering(pipeline):
    train = [
        {"messages": [{"role": "user", "content": "What is the capital of France?"}, {"role": "assistant", "content": "Paris"}]},
        {"messages": [{"role": "user", "content": "Write a python sorting algorithm for integers"}, {"role": "assistant", "content": "def sort(): pass"}]}
    ]
    eval_queries = ["What is the capital of France and Germany?"]
    
    clean, filtered = pipeline.decontaminate_samples(train, eval_queries, n_gram_size=5)
    assert filtered == 1
    assert len(clean) == 1
    assert "sorting algorithm" in clean[0]["messages"][0]["content"]

def test_token_statistics(pipeline):
    samples = [
        {"messages": [{"role": "user", "content": "one two three"}, {"role": "assistant", "content": "four five"}]},
        {"messages": [{"role": "user", "content": "six seven"}, {"role": "assistant", "content": "eight nine ten eleven twelve"}]}
    ]
    stats = pipeline.compute_token_statistics(samples)
    assert stats["count"] == 2
    assert stats["mean"] == 6.0
    assert stats["max"] == 7.0

def test_loss_masking_labels(pipeline):
    sample = {
        "messages": [
            {"role": "system", "content": "You are a code assistant."},
            {"role": "user", "content": "Write hello world"},
            {"role": "assistant", "content": "print('hello world')"}
        ]
    }
    vocab = {"<|im_start|>system": 1, "<|im_start|>user": 2, "<|im_start|>assistant": 3, "<|im_end|>": 4}
    res = pipeline.generate_loss_masked_labels(sample, vocab)
    
    input_ids = res["input_ids"]
    labels = res["labels"]
    assert len(input_ids) == len(labels)
    
    # First part must be masked with -100
    assert labels[0] == -100
    # Assistant response tokens must NOT be -100
    assistant_tokens = [l for l in labels if l != -100]
    assert len(assistant_tokens) > 0
