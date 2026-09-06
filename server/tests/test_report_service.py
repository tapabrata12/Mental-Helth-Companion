import pytest
import asyncio
from src.services.report_service import generate_phq9_report
from src.schemas.assessment import PHQ9AssessmentResult


# 1. Use 'async def' so pytest knows it is an async test
async def test_generate_phq9_report():
    # 2. Prepare your test data
    assessment_data = PHQ9AssessmentResult(
        total_score=14,
        severity="moderate",
        needs_to_follow=True,
        clinical_risk=False,
        recommendation="Please schedule a follow-up."
    )

    # 3. Simply 'await' the async function directly
    result = await generate_phq9_report(assessment_data)
    assert result

