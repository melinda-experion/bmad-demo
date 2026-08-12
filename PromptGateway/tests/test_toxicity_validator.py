from validators.toxicity_validator import ToxicityValidator


def _config():
    return {"enabled": True, "block_threshold": 0.75, "flag_threshold": 0.4}


def test_clean_text_passes():
    validator = ToxicityValidator(_config())
    result = validator.validate("Thank you so much for your help today!")
    assert result.passed is True
    assert result.risk_score == 0.0


def test_profanity_detected_but_below_flag_threshold():
    validator = ToxicityValidator(_config())
    result = validator.validate("This damn printer never works.")
    assert any(f.category == "profanity" for f in result.findings)


def test_self_harm_language_flagged():
    validator = ToxicityValidator(_config())
    result = validator.validate("I want to end my life.")
    assert result.passed is False
    assert result.risk_score >= 75


def test_leetspeak_normalization_catches_obfuscation():
    validator = ToxicityValidator(_config())
    result = validator.validate("you are such an id10t")
    # "id10t" normalizes to "idiot" via leet map (1->i, 0->o)
    assert any(f.category == "harassment" for f in result.findings)
