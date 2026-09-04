from src.schemas.assessment import PHQ9ReportResult, PHQ9AssessmentResult
from src.rag.retriever import retrieve_context
import asyncio
SEVERITY_SEARCH_QUERIES: dict[str, str] = {
    "minimal": "minimal depression symptoms self-care and monitoring",
    "mild": "mild depression symptoms coping strategies",
    "moderate": "moderate depression symptoms diagnostic criteria and treatment",
    "moderately_severe": "moderately severe depression symptoms professional treatment options",
    "severe": "severe depression symptoms clinical intervention and support",
}

async def generate_phq9_report(result: PHQ9AssessmentResult):
    query = SEVERITY_SEARCH_QUERIES[result.severity]
    chunks = await retrieve_context(query, limit=4)
    return chunks

# Dummy code for test
print(asyncio.run(generate_phq9_report(PHQ9AssessmentResult(
    total_score=14,
    severity="moderate",
    needs_to_follow=True,
    clinical_risk=False,
    recommendation="Please schedule a follow-up.",
))))