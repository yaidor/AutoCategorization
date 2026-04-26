import pytest
from pydantic import ValidationError

from app.services.llm.schema import CategorizationResult, EstimatedVolume

VALID_PAYLOAD: dict = {
    "industry": "saas_tech",
    "use_case": "customer_support",
    "interest_level": 4,
    "sentiment": 0.6,
    "urgency": "medium",
    "estimated_volume": {"amount": 500, "period": "weekly"},
    "discovery_channel": "google_search",
    "integration_required": True,
    "systems_mentioned": ["CRM Salesforce", "WhatsApp Business"],
    "main_objection": "Precio",
    "competitors_mentioned": ["Intercom"],
    "personalization_concern": "low",
    "data_sensitivity": "medium",
    "close_probability": 0.7,
    "customer_segment": "midmarket",
    "key_topics": ["automatizacion", "atencion_cliente"],
    "summary_es": "Cliente interesado en automatizar soporte de su SaaS.",
}


def test_valid_payload_parses_with_typed_enums() -> None:
    result = CategorizationResult.model_validate(VALID_PAYLOAD)
    assert result.industry == "saas_tech"
    assert result.urgency == "medium"
    assert result.estimated_volume.period == "weekly"


def test_interest_level_out_of_range_rejected() -> None:
    payload = {**VALID_PAYLOAD, "interest_level": 9}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_sentiment_out_of_range_rejected() -> None:
    payload = {**VALID_PAYLOAD, "sentiment": 2.5}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_close_probability_out_of_range_rejected() -> None:
    payload = {**VALID_PAYLOAD, "close_probability": 1.5}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_unknown_enum_value_rejected() -> None:
    payload = {**VALID_PAYLOAD, "industry": "fintech"}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_uppercase_enum_value_rejected() -> None:
    payload = {**VALID_PAYLOAD, "urgency": "HIGH"}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_missing_required_field_rejected() -> None:
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "summary_es"}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_empty_summary_rejected() -> None:
    payload = {**VALID_PAYLOAD, "summary_es": ""}
    with pytest.raises(ValidationError):
        CategorizationResult.model_validate(payload)


def test_estimated_volume_with_nulls_is_valid() -> None:
    payload = {**VALID_PAYLOAD, "estimated_volume": {"amount": None, "period": None}}
    result = CategorizationResult.model_validate(payload)
    assert result.estimated_volume.amount is None
    assert result.estimated_volume.period is None


def test_extra_fields_are_ignored() -> None:
    payload = {**VALID_PAYLOAD, "hallucinated_field": "ruido"}
    result = CategorizationResult.model_validate(payload)
    assert not hasattr(result, "hallucinated_field")


def test_estimated_volume_standalone_validation() -> None:
    EstimatedVolume.model_validate({"amount": 100, "period": "daily"})
    EstimatedVolume.model_validate({"amount": None, "period": None})
    with pytest.raises(ValidationError):
        EstimatedVolume.model_validate({"amount": 100, "period": "yearly"})
