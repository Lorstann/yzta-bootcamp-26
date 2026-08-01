"""
backend/tests/test_guardrails.py
S16: Keyword guardrail unit tests.
"""

from backend.services.llm.guardrails import check_for_risks


def test_critical_keyword_triggers():
    result = check_for_risks("Artık yaşamak istemiyorum")
    assert result.triggered is True
    assert result.category == "critical"
    assert result.template is not None
    assert "klinik" not in (result.template or "").lower()


def test_dropout_keyword_triggers():
    result = check_for_risks("Bu bootcamp'i bırakıyorum, pes ediyorum")
    assert result.triggered is True
    assert result.category == "dropout"


def test_depression_keyword_triggers():
    result = check_for_risks("Kendimi çok depresifim hissediyorum")
    assert result.triggered is True
    assert result.category == "depression"


def test_turkish_i_normalization():
    result = check_for_risks("İNTİHAR düşünüyorum")
    assert result.triggered is True
    assert result.category == "critical"


def test_normal_message_passthrough():
    result = check_for_risks("Bu hafta enerjim 7, React hooks çalışıyorum")
    assert result.triggered is False
    assert result.category is None
    assert result.template is None


def test_false_positive_edge_partial_word():
    # Should not trigger on unrelated text
    result = check_for_risks("Bugün SQL join pratikleri yaptım")
    assert result.triggered is False
