from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from app.services.llm.schema import CategorizationResult


@dataclass
class LLMResponse:
    parsed: CategorizationResult
    raw: dict[str, Any]


@runtime_checkable
class LLMProvider(Protocol):
    name: str
    model: str

    async def categorize(self, transcript: str) -> LLMResponse: ...


class LLMError(Exception):
    """Base error para fallos de proveedor LLM."""


class LLMValidationError(LLMError):
    """LLM devolvió JSON malformado o que no cumple el schema."""


class LLMRateLimitError(LLMError):
    """Proveedor devolvió 429 / rate limit excedido."""


class LLMTimeoutError(LLMError):
    """Request al proveedor excedió el timeout configurado."""
