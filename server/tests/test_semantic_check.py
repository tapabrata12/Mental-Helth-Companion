from src.services.crisis_service import check_for_crisis_semantic
from unittest.mock import AsyncMock, patch
import pytest

from src.schemas.llm_schema import SemanticCrisisResult
@pytest.mark.asyncio
async def test_semantic_check():
    result = await check_for_crisis_semantic("Seems like it would be better if end my life")
    assert result.crisis_detected == True




@pytest.mark.asyncio
async def test_semantic_detects_crisis_when_llm_says_true():
    fake_response = SemanticCrisisResult(crisis_detected=True, reason="test reason")

    with patch("src.services.crisis_service.get_llm") as mock_get_llm:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = fake_response
        mock_get_llm.return_value = mock_chain

        result = await check_for_crisis_semantic("some text")

        assert result.crisis_detected is True

@pytest.mark.asyncio
async def test_semantic_fails_safe_when_llm_unavailable():
    with patch("src.services.crisis_service.get_llm") as mock_get_llm:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.side_effect = Exception("ResourceExhausted")
        mock_get_llm.return_value = mock_chain

        result = await check_for_crisis_semantic("some text", max_try=1, initial_delay=0.01)

        assert result.crisis_detected is True
        assert "unavailable" in result.reason.lower()