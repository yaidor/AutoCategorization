from app.models import Categorization
from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.prompt import PROMPT_VERSION


def build_categorization(
    meeting_id: int, provider: LLMProvider, response: LLMResponse
) -> Categorization:
    parsed = response.parsed
    return Categorization(
        meeting_id=meeting_id,
        provider=provider.name,
        model=provider.model,
        prompt_version=PROMPT_VERSION,
        raw_json=response.raw,
        industry=parsed.industry,
        use_case=parsed.use_case,
        interest_level=parsed.interest_level,
        sentiment=parsed.sentiment,
        urgency=parsed.urgency,
        volume_amount=parsed.estimated_volume.amount,
        volume_period=parsed.estimated_volume.period,
        discovery_channel=parsed.discovery_channel,
        integration_required=parsed.integration_required,
        systems_mentioned=parsed.systems_mentioned,
        main_objection=parsed.main_objection,
        competitors_mentioned=parsed.competitors_mentioned,
        personalization_concern=parsed.personalization_concern,
        data_sensitivity=parsed.data_sensitivity,
        close_probability=parsed.close_probability,
        customer_segment=parsed.customer_segment,
        key_topics=parsed.key_topics,
        summary_es=parsed.summary_es,
    )
