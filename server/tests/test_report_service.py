import asyncio
from src.schemas.assessment import PHQ9AssessmentResult
from src.services.report_service import generate_phq9_report

fake_result = PHQ9AssessmentResult(
    total_score=14,
    severity="moderate",
    needs_to_follow=True,
    clinical_risk=False,
    recommendation="Please schedule a follow-up.",
)

output = asyncio.run(generate_phq9_report(fake_result))
print(output)
