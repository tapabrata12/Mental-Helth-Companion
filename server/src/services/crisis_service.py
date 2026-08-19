from src.schemas.assessment import CrisisDetectionResult
def check_for_crisis(text: str)->CrisisDetectionResult:
    text_list: list = text.split()
    for item1 in text_list:
        for item2 in actual_phases_list:
            if item1 == item2:
                continue
            else:
                text_list.remove(item1)

    if len(text_list) > 0:
        return CrisisDetectionResult(
            crisis_detected=True,
            matched_phrases=text_list
        )
    return CrisisDetectionResult(
        crisis_detected=False,
        matched_phrases=text_list
    )