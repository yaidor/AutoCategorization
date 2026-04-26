import pytest

from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.providers.mock import MockProvider
from app.services.llm.schema import CategorizationResult


@pytest.mark.asyncio
async def test_mock_provider_satisfies_protocol() -> None:
    provider = MockProvider()
    assert isinstance(provider, LLMProvider)
    assert provider.name == "mock"
    assert provider.model == "mock-deterministic-v1"


@pytest.mark.asyncio
async def test_mock_returns_valid_categorization() -> None:
    provider = MockProvider()
    response = await provider.categorize("Una transcripción de prueba sobre Vambe.")

    assert isinstance(response, LLMResponse)
    assert isinstance(response.parsed, CategorizationResult)
    assert isinstance(response.raw, dict)
    assert response.raw["industry"] == response.parsed.industry.value


@pytest.mark.asyncio
async def test_mock_is_deterministic_for_same_transcript() -> None:
    provider = MockProvider()
    transcript = "El cliente quiere automatizar atención al cliente con Vambe."

    a = await provider.categorize(transcript)
    b = await provider.categorize(transcript)

    assert a.parsed.model_dump() == b.parsed.model_dump()


@pytest.mark.asyncio
async def test_mock_varies_across_different_transcripts() -> None:
    provider = MockProvider()
    a = await provider.categorize("Transcripción A sobre logística.")
    b = await provider.categorize("Transcripción B sobre salud.")

    assert a.parsed.model_dump() != b.parsed.model_dump()


@pytest.mark.asyncio
async def test_mock_raw_is_json_serializable() -> None:
    import json

    provider = MockProvider()
    response = await provider.categorize("Texto cualquiera.")
    serialized = json.dumps(response.raw)
    assert "industry" in serialized
