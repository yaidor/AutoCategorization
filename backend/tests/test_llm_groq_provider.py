import json
from collections.abc import Callable

import httpx
import pytest

from app.services.llm.base import (
    LLMError,
    LLMRateLimitError,
    LLMValidationError,
)
from app.services.llm.providers.groq import GroqProvider

VALID_LLM_OUTPUT: dict = {
    "industry": "saas_tech",
    "use_case": "customer_support",
    "interest_level": 4,
    "sentiment": 0.6,
    "urgency": "medium",
    "estimated_volume": {"amount": 500, "period": "weekly"},
    "discovery_channel": "google_search",
    "integration_required": True,
    "systems_mentioned": ["CRM"],
    "main_objection": None,
    "competitors_mentioned": [],
    "personalization_concern": "low",
    "data_sensitivity": "medium",
    "close_probability": 0.7,
    "customer_segment": "midmarket",
    "key_topics": ["automatizacion"],
    "summary_es": "Cliente SaaS interesado en automatizar soporte.",
}


def _chat_response(payload: dict, status: int = 200) -> httpx.Response:
    body = {
        "choices": [
            {"message": {"content": json.dumps(payload)}, "index": 0, "finish_reason": "stop"}
        ]
    }
    return httpx.Response(status_code=status, json=body)


def _make_transport(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _provider_with(
    handler: Callable[[httpx.Request], httpx.Response], **kwargs: object
) -> GroqProvider:
    return GroqProvider(
        api_key="test-key",
        max_attempts=kwargs.pop("max_attempts", 3),
        wait_min_seconds=0.0,
        wait_max_seconds=0.0,
        max_concurrent=10,
        transport=_make_transport(handler),
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_happy_path_returns_parsed_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    response = await provider.categorize("transcripción de prueba")

    assert response.parsed.industry == "saas_tech"
    assert response.parsed.close_probability == 0.7
    assert response.raw["summary_es"].startswith("Cliente SaaS")


@pytest.mark.asyncio
async def test_rejects_missing_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        GroqProvider(api_key="")


@pytest.mark.asyncio
async def test_rate_limit_then_success() -> None:
    calls = {"n": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, text="rate limit hit")
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    response = await provider.categorize("texto")
    assert response.parsed.industry == "saas_tech"
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_rate_limit_exhausts_attempts() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="still limited")

    provider = _provider_with(handler, max_attempts=2)
    with pytest.raises(LLMRateLimitError):
        await provider.categorize("texto")


@pytest.mark.asyncio
async def test_5xx_treated_as_retryable() -> None:
    calls = {"n": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, text="service unavailable")
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    response = await provider.categorize("texto")
    assert response.parsed.industry == "saas_tech"
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_4xx_non_429_not_retried() -> None:
    calls = {"n": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(401, text="unauthorized")

    provider = _provider_with(handler)
    with pytest.raises(LLMError):
        await provider.categorize("texto")
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_invalid_json_triggers_reprompt_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return (
                _chat_response({}, status=200)
                if False
                else httpx.Response(
                    200,
                    json={
                        "choices": [
                            {
                                "message": {"content": "no soy json válido {"},
                                "index": 0,
                                "finish_reason": "stop",
                            }
                        ]
                    },
                )
            )
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    response = await provider.categorize("texto")
    assert response.parsed.industry == "saas_tech"
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_schema_invalid_triggers_reprompt_then_succeeds() -> None:
    calls = {"n": 0}
    bad_payload = {**VALID_LLM_OUTPUT, "interest_level": 99}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return _chat_response(bad_payload)
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    response = await provider.categorize("texto")
    assert response.parsed.interest_level == 4
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_schema_invalid_twice_raises_validation_error() -> None:
    bad_payload = {**VALID_LLM_OUTPUT, "industry": "fintech"}

    def handler(_: httpx.Request) -> httpx.Response:
        return _chat_response(bad_payload)

    provider = _provider_with(handler)
    with pytest.raises(LLMValidationError):
        await provider.categorize("texto")


@pytest.mark.asyncio
async def test_authorization_header_uses_bearer_token() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization", "")
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    await provider.categorize("texto")
    assert captured["auth"] == "Bearer test-key"


@pytest.mark.asyncio
async def test_request_uses_json_mode() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return _chat_response(VALID_LLM_OUTPUT)

    provider = _provider_with(handler)
    await provider.categorize("texto")
    body = captured["body"]
    assert isinstance(body, dict)
    assert body["response_format"] == {"type": "json_object"}
    assert body["model"] == "llama-3.3-70b-versatile"
    assert body["temperature"] == 0.0
