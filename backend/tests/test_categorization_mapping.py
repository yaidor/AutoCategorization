from app.services.categorization.mapping import build_categorization
from app.services.llm.base import LLMResponse
from app.services.llm.prompt import PROMPT_VERSION
from app.services.llm.providers.mock import MockProvider
from app.services.llm.schema import CategorizationResult, EstimatedVolume


def _sample_result() -> CategorizationResult:
    return CategorizationResult(
        industry="saas_tech",
        use_case="customer_support",
        interest_level=4,
        sentiment=0.6,
        urgency="medium",
        estimated_volume=EstimatedVolume(amount=500, period="weekly"),
        discovery_channel="google_search",
        integration_required=True,
        systems_mentioned=["CRM Salesforce"],
        main_objection=None,
        competitors_mentioned=[],
        personalization_concern="low",
        data_sensitivity="medium",
        close_probability=0.7,
        customer_segment="midmarket",
        key_topics=["automatizacion"],
        summary_es="Resumen de prueba.",
    )


def test_mapping_copies_fields_and_sets_provenance() -> None:
    parsed = _sample_result()
    response = LLMResponse(parsed=parsed, raw=parsed.model_dump(mode="json"))
    provider = MockProvider()

    cat = build_categorization(meeting_id=42, provider=provider, response=response)

    assert cat.meeting_id == 42
    assert cat.provider == "mock"
    assert cat.model == "mock-deterministic-v1"
    assert cat.prompt_version == PROMPT_VERSION
    assert cat.industry == "saas_tech"
    assert cat.use_case == "customer_support"
    assert cat.volume_amount == 500
    assert cat.volume_period == "weekly"
    assert cat.summary_es == "Resumen de prueba."


def test_mapping_handles_null_volume() -> None:
    parsed = _sample_result()
    parsed.estimated_volume = EstimatedVolume(amount=None, period=None)
    response = LLMResponse(parsed=parsed, raw=parsed.model_dump(mode="json"))

    cat = build_categorization(meeting_id=1, provider=MockProvider(), response=response)

    assert cat.volume_amount is None
    assert cat.volume_period is None


def test_mapping_preserves_raw_json_with_extras() -> None:
    parsed = _sample_result()
    raw = {**parsed.model_dump(mode="json"), "extra_field": "ruido del LLM"}
    response = LLMResponse(parsed=parsed, raw=raw)

    cat = build_categorization(meeting_id=1, provider=MockProvider(), response=response)

    assert cat.raw_json["extra_field"] == "ruido del LLM"
    assert cat.raw_json["industry"] == "saas_tech"


def test_mapping_handles_empty_lists() -> None:
    parsed = _sample_result()
    parsed.systems_mentioned = []
    parsed.competitors_mentioned = []
    parsed.key_topics = []
    response = LLMResponse(parsed=parsed, raw=parsed.model_dump(mode="json"))

    cat = build_categorization(meeting_id=1, provider=MockProvider(), response=response)

    assert cat.systems_mentioned == []
    assert cat.competitors_mentioned == []
    assert cat.key_topics == []
