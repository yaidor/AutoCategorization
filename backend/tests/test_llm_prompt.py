from app.services.llm.prompt import (
    PROMPT_VERSION,
    SCHEMA_SUMMARY,
    SYSTEM_PROMPT,
    build_user_prompt,
)


def test_prompt_version_is_v1() -> None:
    assert PROMPT_VERSION == "v1"


def test_user_prompt_includes_transcript() -> None:
    transcript = "Texto único de la reunión 12345."
    prompt = build_user_prompt(transcript)
    assert transcript in prompt


def test_system_prompt_embeds_schema() -> None:
    assert SCHEMA_SUMMARY in SYSTEM_PROMPT


def test_system_prompt_lists_critical_enums() -> None:
    for token in (
        "financial_services",
        "customer_support",
        "smb",
        "midmarket",
        "enterprise",
        "low",
        "medium",
        "high",
    ):
        assert token in SYSTEM_PROMPT
