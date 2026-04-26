from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.providers.groq import GroqProvider
from app.services.llm.providers.mock import MockProvider


def get_llm_provider() -> LLMProvider:
    name = settings.llm_provider.lower().strip()
    if name == "mock":
        return MockProvider()
    if name == "groq":
        return GroqProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model or None,
        )
    raise ValueError(
        f"Provider LLM no soportado: {settings.llm_provider!r}. Disponibles: 'mock', 'groq'."
    )
