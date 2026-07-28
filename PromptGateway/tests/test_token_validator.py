from validators.token_validator import TokenValidator


def test_short_prompt_within_limits():
    validator = TokenValidator({"max_prompt_tokens": 100, "warn_prompt_tokens": 50})
    result = validator.validate("Hello, how are you today?")
    assert result.passed is True
    assert result.risk_score == 0.0


def test_prompt_exceeding_max_tokens_fails():
    validator = TokenValidator({"max_prompt_tokens": 5, "warn_prompt_tokens": 2})
    long_text = "word " * 200
    result = validator.validate(long_text)
    assert result.passed is False
    assert any(f.name == "token_limit_exceeded" for f in result.findings)


def test_prompt_in_warn_band():
    validator = TokenValidator({"max_prompt_tokens": 1000, "warn_prompt_tokens": 2})
    text = "word " * 20
    result = validator.validate(text)
    assert result.passed is True
    assert any(f.name == "token_limit_warning" for f in result.findings)


def test_count_tokens_returns_positive_int():
    validator = TokenValidator({})
    assert validator.count_tokens("hello world") > 0
