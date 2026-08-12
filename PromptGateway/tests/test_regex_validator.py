from config import load_policy
from validators.regex_validator import RegexValidator


def _rules():
    return load_policy().get("regex_rules", [])


def test_clean_prompt_passes():
    validator = RegexValidator(_rules())
    result = validator.validate("What is the capital of France?")
    assert result.passed is True
    assert result.risk_score == 0.0


def test_sql_injection_detected():
    validator = RegexValidator(_rules())
    result = validator.validate("'; DROP TABLE users; --")
    assert result.passed is False
    assert any(f.category == "sql_injection" for f in result.findings)


def test_private_key_detected():
    validator = RegexValidator(_rules())
    result = validator.validate("-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA\n-----END RSA PRIVATE KEY-----")
    assert result.passed is False
    assert any(f.category == "secret_leak" for f in result.findings)
    assert result.risk_score >= 90
