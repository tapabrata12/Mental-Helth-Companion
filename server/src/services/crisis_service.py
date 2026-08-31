import asyncio
import logging
import random
from typing import Any, Sequence, cast

from google.genai.errors import ServerError
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


def get_llm_object() -> (
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


async def check_for_crisis_semantic(
    text: str, max_try: int = 3, initial_delay: float = 1.0
) -> SemanticCrisisResult:
    """Checks for mental health crisis using Gemini with exponential backoff and jitter."""
    delay = initial_delay

    for attempt in range(max_try):
        try:
            crisis_chain = get_llm_object()
            response = await crisis_chain.ainvoke({"text": text})

            return cast(SemanticCrisisResult, response)

        except Exception as e:
            # Dynamically look up status attributes across multiple package types
            status_code = getattr(e, "code", None) or getattr(e, "status_code", None)
            error_str = str(e)

            # Detect whether it is a Rate Limit (429) or High Demand Server Error (503)
            is_transient = (
                status_code in (429, 503)
                or "ResourceExhausted" in error_str
                or "ServiceUnavailable" in error_str
                or isinstance(e, ServerError)
            )

            if is_transient:
                current_attempt = attempt + 1
                error_label = "429 Rate Limit" if (status_code == 429 or "ResourceExhausted" in error_str) else "503 High Demand"

                if current_attempt == max_try:
                    logging.error(
                        f"Gemini API {error_label} failed permanently after {max_try} attempts."
                    )
                    break  # Drop out of the loop to trigger the safe fallback response below

                logging.warning(
                    f"Gemini API {error_label} (Attempt {current_attempt}/{max_try}). "
                    f"Retrying in {delay:.2f} seconds..."
                )
                await asyncio.sleep(delay)
                delay = (delay * 2) + random.uniform(0.1, 0.4)
            else:
                # Instantly bubble up actual code bugs (like 401 Unauthorized or 400 Bad syntax)
                logging.exception("Non-recoverable error during semantic crisis classification.")
                raise e

    # FALL-SAFE CRITICAL STATE MANAGEMENT
    logging.critical(
        "Semantic crisis detection unavailable. Triggering system-wide safety fallback."
    )
    return SemanticCrisisResult(
        crisis_detected=True,
        reason="Crisis classification service temporarily offline - failing safe.",
    )

"""
###################################################################################################################################################
                                                                        Main Function
Signature: String                                                                                               Return: Pydantic Base Model
###################################################################################################################################################
"""
def check_for_crisis(text: str) -> CrisisDetectionResult:
    """Keyword pattern matching backup for fast fallback verification."""
    text_lower = text.lower()
    matched: list[str] = []

    for i in CRISIS_PHRASES:
        if i.lower() in text_lower:
            matched.append(i)

    if matched:
        return CrisisDetectionResult(
            crisis_detected=True, matched_phrases=matched
        )

    return CrisisDetectionResult(
        crisis_detected=False, matched_phrases=matched
    )


if __name__ == "__main__":
    test_result = asyncio.run(check_for_crisis_semantic("Hello how are you?"))
    print(test_result)
