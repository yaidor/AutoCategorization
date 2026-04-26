import asyncio
import json
from typing import Any

import httpx
import structlog
from pydantic import ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.services.llm.base import (
    LLMError,
    LLMRateLimitError,
    LLMResponse,
    LLMTimeoutError,
    LLMValidationError,
)
from app.services.llm.prompt import SYSTEM_PROMPT, build_user_prompt
from app.services.llm.schema import CategorizationResult

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

log = structlog.get_logger()


class GroqProvider:
    name: str = "groq"

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_concurrent: int | None = None,
        max_attempts: int = 3,
        wait_min_seconds: float = 1.0,
        wait_max_seconds: float = 8.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Groq API key requerida (settings.llm_api_key vacío)")
        self._api_key = api_key
        self.model = model or DEFAULT_MODEL
        self._timeout = (
            timeout_seconds if timeout_seconds is not None else settings.llm_timeout_seconds
        )
        self._semaphore = asyncio.Semaphore(
            max_concurrent if max_concurrent is not None else settings.llm_max_concurrent
        )
        self._max_attempts = max_attempts
        self._wait_min = wait_min_seconds
        self._wait_max = wait_max_seconds
        self._transport = transport

    async def _post(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}

        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            try:
                response = await client.post(GROQ_ENDPOINT, json=payload, headers=headers)
            except httpx.TimeoutException as exc:
                raise LLMTimeoutError(f"Timeout tras {self._timeout}s") from exc
            except httpx.HTTPError as exc:
                raise LLMError(f"Error HTTP: {exc}") from exc

        if response.status_code == 429:
            raise LLMRateLimitError(f"Rate limit: {response.text[:200]}")
        if response.status_code >= 500:
            raise LLMRateLimitError(f"Groq {response.status_code}: {response.text[:200]}")
        if response.status_code >= 400:
            raise LLMError(f"Groq {response.status_code}: {response.text[:200]}")

        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise LLMError(f"Body no es JSON: {response.text[:200]}") from exc

    def _extract_content(self, body: dict[str, Any]) -> str:
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMValidationError(f"Estructura de respuesta inesperada: {body}") from exc
        if not isinstance(content, str):
            raise LLMValidationError(f"Content no es string: {content!r}")
        return content

    def _parse_and_validate(self, content: str) -> tuple[CategorizationResult, dict[str, Any]]:
        try:
            raw = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMValidationError(f"JSON malformado: {exc}") from exc

        if not isinstance(raw, dict):
            raise LLMValidationError(f"Respuesta no es objeto JSON: {raw!r}")

        try:
            parsed = CategorizationResult.model_validate(raw)
        except ValidationError as exc:
            errors_summary = "; ".join(
                f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()[:5]
            )
            raise LLMValidationError(f"Schema inválido: {errors_summary}") from exc

        return parsed, raw

    async def _categorize_once(self, transcript: str, error_feedback: str = "") -> LLMResponse:
        user_msg = build_user_prompt(transcript)
        if error_feedback:
            user_msg += (
                "\n\nIMPORTANTE: tu respuesta anterior no fue válida. "
                f"Error: {error_feedback[:500]}\n"
                "Devuelve SOLO un objeto JSON que cumpla el schema, sin texto adicional."
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        body = await self._post(messages)
        content = self._extract_content(body)
        parsed, raw = self._parse_and_validate(content)
        return LLMResponse(parsed=parsed, raw=raw)

    async def _with_network_retries(self, transcript: str, error_feedback: str = "") -> LLMResponse:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=1, min=self._wait_min, max=self._wait_max),
            retry=retry_if_exception_type((LLMRateLimitError, LLMTimeoutError)),
            reraise=True,
        ):
            with attempt:
                return await self._categorize_once(transcript, error_feedback)
        raise RuntimeError("retry loop terminó sin resultado")

    async def categorize(self, transcript: str) -> LLMResponse:
        async with self._semaphore:
            try:
                return await self._with_network_retries(transcript)
            except LLMValidationError as first_error:
                log.warning(
                    "groq_response_invalid_retrying",
                    error=str(first_error)[:200],
                )
                return await self._with_network_retries(transcript, error_feedback=str(first_error))
