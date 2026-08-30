import pytest
from examples.data_privacy import PIITokenVault, DifferentialPrivacyEngine

def test_pii_tokenization_and_detokenization():
    vault = PIITokenVault()
    raw_prompt = "Contact user@example.com with SSN 123-45-6789 and Card 1111-2222-3333-4444."
    
    tokenized = vault.tokenize_text(raw_prompt)
    assert "user@example.com" not in tokenized
    assert "123-45-6789" not in tokenized
    assert "1111-2222-3333-4444" not in tokenized
    assert "<EMAIL_1>" in tokenized
    assert "<SSN_1>" in tokenized
    assert "<CREDIT_CARD_1>" in tokenized
    
    # Detokenize
    restored = vault.detokenize_text(tokenized)
    assert restored == raw_prompt

def test_right_to_be_forgotten_key_shredding():
    vault = PIITokenVault()
    raw = "User email: secret@corp.org"
    tokenized = vault.tokenize_text(raw)
    
    # Delete secret@corp.org
    deleted = vault.forget_user_pii("secret@corp.org")
    assert deleted is True
    
    # Detokenizing now leaves surrogate tag intact
    after_forget = vault.detokenize_text(tokenized)
    assert "secret@corp.org" not in after_forget
    assert "<EMAIL_1>" in after_forget

def test_differential_privacy_laplace_noise():
    # Epsilon=1.0, sensitivity=10.0
    val = 1000.0
    noisy = DifferentialPrivacyEngine.laplace_mechanism(val, sensitivity=10.0, epsilon=1.0)
    assert isinstance(noisy, float)
    # Laplace noise is centered at 0 with high probability inside [-100, 100]
    assert 800.0 < noisy < 1200.0

def test_invalid_epsilon_raises_error():
    with pytest.raises(ValueError):
        DifferentialPrivacyEngine.laplace_mechanism(100.0, sensitivity=1.0, epsilon=0.0)
    with pytest.raises(ValueError):
        DifferentialPrivacyEngine.laplace_mechanism(100.0, sensitivity=1.0, epsilon=-0.5)

def test_multiple_identical_entities_share_surrogate():
    vault = PIITokenVault()
    text = "Email same@test.com twice: same@test.com"
    tokenized = vault.tokenize_text(text)
    
    assert tokenized == "Email <EMAIL_1> twice: <EMAIL_1>"
    assert len(vault.forward_map) == 1
