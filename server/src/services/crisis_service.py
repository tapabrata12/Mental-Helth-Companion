from src.schemas.assessment import CrisisDetectionResult
from src.core.crisis_phrases import CRISIS_PHRASES

def check_for_crisis(text: str)-> CrisisDetectionResult:
    text_lower = text.lower()
    matched: list[str] = []

    for i in CRISIS_PHRASES:
        if i.lower() in text_lower:
            matched.append(i)
    if matched:
        return CrisisDetectionResult(crisis_detected=True, matched_phrases=matched)

    return CrisisDetectionResult(crisis_detected=False, matched_phrases=matched)