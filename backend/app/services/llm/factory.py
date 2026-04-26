from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.providers.mock import MockProvider


def get_llm_provider() -> LLMProvider:
    name = settings.llm_provider.lower().strip()
    if name == "mock":
        return MockProvider()
    raise ValueError(f"Provider LLM no soportado: {settings.llm_provider!r}. Disponibles: 'mock'.")
