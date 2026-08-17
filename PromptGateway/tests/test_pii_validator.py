from config import load_policy
from validators.pii_validator import PIIValidator


def _rules():
    return load_policy().get("pii_rules", {})


def test_no_pii_passes():
    validator = PIIValidator(_rules())
    result = validator.validate("Please summarize this quarterly report.")
    assert result.passed is True


def test_email_detected():
    validator = PIIValidator(_rules())
    result = validator.validate("Contact me at jane.doe@example.com for details.")
    assert result.passed is False
    assert any(f.category == "pii_email" for f in result.findings)


def test_valid_credit_card_detected():
    validator = PIIValidator(_rules())
    # 4111111111111111 is a well-known Luhn-valid test Visa number.
    result = validator.validate("My card number is 4111111111111111 please charge it")
    assert result.passed is False
    assert any(f.category == "credit_card" for f in result.findings)


def test_invalid_card_like_number_not_flagged_as_credit_card():
    validator = PIIValidator(_rules())
    result = validator.validate("Order id is 1234567890123456")  # fails Luhn
    assert not any(f.category == "credit_card" for f in result.findings)


def test_aws_key_detected():
    validator = PIIValidator(_rules())
    result = validator.validate("key: AKIAIOSFODNN7EXAMPLE")
    assert result.passed is False
    assert any(f.category == "secret_leak" for f in result.findings)


def test_redact_masks_email():
    validator = PIIValidator(_rules())
    redacted = validator.redact("Email jane.doe@example.com now")
    assert "jane.doe@example.com" not in redacted
    assert "REDACTED_EMAIL" in redacted


def test_anthropic_style_key_detected():
    validator = PIIValidator(_rules())
    result = validator.validate(
        "Use my API key sk-ant-api03-AAAA1111BBBB2222CCCC3333DDDD4444 to call the model."
    )
    assert result.passed is False
    assert any(f.category == "secret_leak" for f in result.findings)


def test_stripe_style_underscored_key_detected():
    validator = PIIValidator(_rules())
    result = validator.validate("publishable key pk_live_51H8xxxxxxxxxxxxxxxxxxxxxxxxxxxx set")
    assert result.passed is False
    assert any(f.category == "secret_leak" for f in result.findings)


def test_generic_key_prefix_requires_digit_to_avoid_prose_false_positive():
    validator = PIIValidator(_rules())
    result = validator.validate("Our key-value-store-implementation-details doc is outdated")
    assert not any(f.category == "secret_leak" for f in result.findings)
