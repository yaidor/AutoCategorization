from app.services.llm.prompt import (
    PROMPT_VERSION,
    SCHEMA_SUMMARY,
    SYSTEM_PROMPT,
    build_user_prompt,
)


def test_prompt_version_is_set() -> None:
    assert PROMPT_VERSION
    assert PROMPT_VERSION.startswith("v")


def test_system_prompt_includes_calibration_anchors() -> None:
    for token in ("close_probability", "0.70 por default", "anclas concretas"):
        assert token.lower() in SYSTEM_PROMPT.lower()


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
