from src.schemas.assessment import CrisisDetectionResult,CrisisResource,PHQ9CrisisSupport
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


def build_crisis_support(crisis_detection_flag: bool) -> PHQ9CrisisSupport | None:  # Build structured crisis resources when PHQ-9 item 9 signals risk
    if not crisis_detection_flag:  # Check whether the assessment needs crisis support
        return None  # Return no crisis object when the assessment did not trigger risk

    return PHQ9CrisisSupport(  # Return a structured safety payload the frontend can display immediately
        crisis_detected=True,  # Mark that normal assessment/report flow should pause
        message="Your answer suggests possible self-harm risk. Please contact emergency services or a crisis helpline now, and reach out to someone you trust.",  # Provide safety-first wording
        resources=[  # Provide India-focused resources from the project specification
            CrisisResource(name="iCall India", contact="9152987821", region="India"),  # Add iCall India helpline details
            CrisisResource(name="Vandrevala Foundation", contact="1860-2662-345", region="India"),  # Add Vandrevala Foundation helpline details
            CrisisResource(name="Local emergency services", contact="Contact your local emergency number immediately if you are in immediate danger", region="Local"),  # Add emergency escalation guidance
        ],  # Finish crisis resource list
    )  # Finish crisis support object creation