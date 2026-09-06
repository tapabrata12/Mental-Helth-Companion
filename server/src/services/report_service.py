from typing import Any, Sequence

from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import  RunnableSerializable

from src.schemas.assessment import PHQ9ReportResult, PHQ9AssessmentResult
from src.rag.retriever import retrieve_context
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings

SEVERITY_SEARCH_QUERIES: dict[str, str] = {
    "minimal": "minimal depression symptoms self-care and monitoring",
    "mild": "mild depression symptoms coping strategies",
    "moderate": "moderate depression symptoms diagnostic criteria and treatment",
    "moderately_severe": "moderately severe depression symptoms professional treatment options",
    "severe": "severe depression symptoms clinical intervention and support",
}

def _format_context(chunks: list[dict]) -> str:
    formatted_string = ""
    for chunk in chunks:
        source: str = chunk['source_document']
        text: str = chunk['text']
        formatted_string += f"Source document: {source}\n Important Text: \"{text}\"\n\n"
    return formatted_string

async def generate_phq9_report(result: PHQ9AssessmentResult):
    query = SEVERITY_SEARCH_QUERIES[result.severity]
    chunks = await retrieve_context(query, limit=10)
    return chunks

async def _get_report_llm() -> RunnableSerializable[PromptValue | str | Sequence[Any], PromptValue]:
    llm = ChatNVIDIA(
        model=settings.NVIDIA_CHAT_MODEL,
        api_key= settings.NVIDIA_API_KEY,
        temperature=0.3,
        top_p=0.95,
        max_tokens=16384,
        # extra_body={"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
    )
    structured_llm = llm.with_structured_output(PHQ9ReportResult)

    report_prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
    "You are a supportive mental health report writer for a wellness app, not a clinician. "
    "Base your writing ONLY on the provided source context below — do not invent clinical claims "
    "or add information not grounded in that context. "
    "Write a plain-language explanation of what the person's results may suggest, using warm, "
    "non-alarming language. Also suggest a few practical, general coping tips (e.g. breathing "
    "exercises, sleep hygiene, gentle self-care) grounded in the source material where possible. "
    "Never state a definitive diagnosis — always frame things as possibilities, and encourage "
    "professional consultation when appropriate."
    )),

    ("human","PHQ-9 Severity: {severity}\nPHQ-9 Total Score: {total_score}\n\nRelevant source material:\n{context}")
    ])

    return structured_llm | report_prompt_template