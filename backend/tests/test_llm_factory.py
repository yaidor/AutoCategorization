import pytest

from app.core.config import settings
from app.services.llm.factory import get_llm_provider
from app.services.llm.providers.groq import GroqProvider
from app.services.llm.providers.mock import MockProvider


def test_factory_returns_mock_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "mock")
    assert isinstance(get_llm_provider(), MockProvider)


def test_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "unobtanium")
    with pytest.raises(ValueError, match="no soportado"):
        get_llm_provider()


def test_factory_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "MOCK")
    assert isinstance(get_llm_provider(), MockProvider)


def test_factory_returns_groq_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "groq")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", "")
    provider = get_llm_provider()
    assert isinstance(provider, GroqProvider)
    assert provider.model == "llama-3.3-70b-versatile"


def test_factory_groq_uses_configured_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "groq")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", "mixtral-8x7b-32768")
    provider = get_llm_provider()
    assert isinstance(provider, GroqProvider)
    assert provider.model == "mixtral-8x7b-32768"


def test_factory_groq_rejects_empty_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "groq")
    monkeypatch.setattr(settings, "llm_api_key", "")
    with pytest.raises(ValueError, match="API key"):
        get_llm_provider()
