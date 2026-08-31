from src.services.crisis_service import check_for_crisis

def test_crisis_service():
    text = "Sometimes I feel like everyone would just move on fine if I stopped showing up."
    text = text.lower()
    result = check_for_crisis(text)
    assert result.crisis_detected == True
    assert text in result.matched_phrases