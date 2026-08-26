from src.services.crisis_service import check_for_crisis

def test_crisis_service():
    text = "I want to kill myself"
    text = text.lower()
    result = check_for_crisis(text)
    assert result.crisis_detected == True
    assert text in result.matched_phrases