import hashlib
import random

from app.models.enums import (
    CustomerSegment,
    DataSensitivity,
    DiscoveryChannel,
    Industry,
    PersonalizationConcern,
    Urgency,
    UseCase,
    VolumePeriod,
)
from app.services.llm.base import LLMResponse
from app.services.llm.schema import CategorizationResult, EstimatedVolume

_SYSTEMS = ["CRM Salesforce", "WhatsApp Business", "Shopify", "Zendesk", "HubSpot", "ERP SAP"]
_OBJECTIONS = [
    "Precio percibido como alto",
    "Implementación compleja",
    "Personalización limitada",
    "Tiempo de onboarding",
    None,
    None,
]
_COMPETITORS = ["Intercom", "Drift", "ManyChat", "Tidio", "Chatfuel"]
_TOPICS = [
    "automatizacion",
    "atencion_cliente",
    "integracion_crm",
    "escalamiento",
    "soporte_24_7",
    "personalizacion",
    "reduccion_costos",
]


class MockProvider:
    name: str = "mock"
    model: str = "mock-deterministic-v1"

    async def categorize(self, transcript: str) -> LLMResponse:
        seed = int(hashlib.sha256(transcript.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)

        result = CategorizationResult(
            industry=rng.choice(list(Industry)),
            use_case=rng.choice(list(UseCase)),
            interest_level=rng.randint(1, 5),
            sentiment=round(rng.uniform(-1.0, 1.0), 2),
            urgency=rng.choice(list(Urgency)),
            estimated_volume=EstimatedVolume(
                amount=rng.choice([None, 100, 500, 1000, 5000, 10000]),
                period=rng.choice([None, *list(VolumePeriod)]),
            ),
            discovery_channel=rng.choice(list(DiscoveryChannel)),
            integration_required=rng.choice([True, False]),
            systems_mentioned=rng.sample(_SYSTEMS, k=rng.randint(0, 3)),
            main_objection=rng.choice(_OBJECTIONS),
            competitors_mentioned=rng.sample(_COMPETITORS, k=rng.randint(0, 2)),
            personalization_concern=rng.choice(list(PersonalizationConcern)),
            data_sensitivity=rng.choice(list(DataSensitivity)),
            close_probability=round(rng.uniform(0.0, 1.0), 2),
            customer_segment=rng.choice(list(CustomerSegment)),
            key_topics=rng.sample(_TOPICS, k=rng.randint(1, 4)),
            summary_es=(
                "Cliente B2B explorando automatización de atención al cliente con Vambe; "
                f"volumen estimado {rng.choice(['bajo', 'medio', 'alto'])}."
            ),
        )

        return LLMResponse(parsed=result, raw=result.model_dump(mode="json"))
