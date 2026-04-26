import pytest

from app.core.config import settings
from app.services.llm.factory import get_llm_provider
from app.services.llm.providers.mock import MockProvider


def test_factory_returns_mock_by_default() -> None:
    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)


def test_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "unobtanium")
    with pytest.raises(ValueError, match="no soportado"):
        get_llm_provider()


def test_factory_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "MOCK")
    assert isinstance(get_llm_provider(), MockProvider)
