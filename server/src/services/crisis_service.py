import asyncio
import logging
import random
from typing import Any, Sequence

from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from src.core.config import settings
from src.core.crisis_phrases import CRISIS_PHRASES
from src.schemas.assessment import (
    CrisisDetectionResult,
    CrisisResource,
    PHQ9CrisisSupport,
)
from src.schemas.llm_schema import SemanticCrisisResult


def build_crisis_support(crisis_detection_flag: bool) -> PHQ9CrisisSupport | None:
    """Build structured crisis resources when a risk is signaled."""
    if not crisis_detection_flag:
        return None

    return PHQ9CrisisSupport(
        crisis_detected=True,
        message=(
            "Your answer suggests possible self-harm risk. Please contact emergency services "
            "or a crisis helpline now, and reach out to someone you trust."
        ),
        resources=[
            CrisisResource(
                name="iCall India", contact="9152987821", region="India"
            ),
            CrisisResource(
                name="Vandrevala Foundation",
                contact="1860-2662-345",
                region="India",
            ),
            CrisisResource(
                name="Local emergency services",
                contact="Contact your local emergency number immediately if you are in immediate danger",
                region="Local",
            ),
        ],
    )
# Whether my error is worth to be wait and resolvable

def _check_for_right_status_code(e: Exception) -> bool:
    status_code = getattr(e, "code", None) or getattr(e, "status_code", None)
    exp_str = str(e)

    return status_code in (429, 503) or "ResourceExhausted" in exp_str or "ServiceUnavailable" in exp_str


async def get_llm() -> (
    Runnable[PromptValue | str | Sequence[Any], BaseModel | Any]
):
    """Initializes and returns the structured LangChain classification chain."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.0,
    )
    structured_llm = llm.with_structured_output(SemanticCrisisResult)

    crisis_prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a safety classifier for a mental health app. "
                "Given a user's message, determine if it suggests risk of suicide, self-harm, or a mental health crisis. "
                "Be sensitive — if there is any reasonable chance of risk, mark crisis_detected as true."
            ),
        ),
        ("human", 'Message: "{text}"'),
    ])

    return crisis_prompt_template | structured_llm


async def check_for_crisis_semantic(text: str, max_try: int = 3, initial_delay: float = 1.0) -> SemanticCrisisResult:
    """Checks for mental health crisis using Gemini with exponential backoff and jitter."""
    delay = initial_delay

    # Call the Chain
    crisis_chain = await get_llm()
    for attempt in range(max_try):
        try:
            result = await crisis_chain.ainvoke({"text": text})
            return result
        except Exception as e:
            if _check_for_right_status_code(e):
                await asyncio.sleep(delay)
                logging.warning(f"Trying our internal server error: {attempt} / {max_try}")
                delay = (delay * 2) + random.uniform(0.3, 0.6)
            else:
                logging.warning(f"Client side problem may be API or internal configuration cannot connect to the services automatically: {e}")
                raise e
    return SemanticCrisisResult(crisis_detected=True, reason="Crisis classification service temporarily unavailable — failing safe.")

"""
###################################################################################################################################################
                                                                        Main Function
Signature: String                                                                                               Return: Pydantic Base Model
###################################################################################################################################################
"""
async def check_for_crisis(text: str) -> CrisisDetectionResult | SemanticCrisisResult:
    """Keyword pattern matching backup for fast fallback verification."""
    text_lower = text.lower()
    matched: list[str] = []

    for i in CRISIS_PHRASES:
        if i.lower() in text_lower:
            matched.append(i)

    semantic_crisis_result = await check_for_crisis_semantic(text=text)
    crisis_detected = True if matched or semantic_crisis_result.crisis_detected else False
    if not matched:
        return SemanticCrisisResult(crisis_detected = crisis_detected, reason = semantic_crisis_result.reason)
    return CrisisDetectionResult(crisis_detected=crisis_detected, matched_phrases=matched)



# if __name__ == "__main__":
#     # test_result = asyncio.run(check_for_crisis_semantic("Hello how are you?"))
#     test_result = asyncio.run(check_for_crisis("Don't know why it fells that is life has no meaning"))
#     print(test_result)
