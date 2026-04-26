PROMPT_VERSION = "v1"


SCHEMA_SUMMARY = """{
  "industry": "financial_services|healthcare|retail_ecommerce|education|logistics|hospitality|real_estate|saas_tech|legal|marketing|manufacturing|nonprofit|other",
  "use_case": "customer_support|technical_support|sales_inquiries|bookings_reservations|logistics_tracking|internal_ops|other",
  "interest_level": "int 1..5",
  "sentiment": "float -1..1",
  "urgency": "low|medium|high",
  "estimated_volume": { "amount": "int|null", "period": "daily|weekly|monthly|null" },
  "discovery_channel": "conference|referral|google_search|linkedin|podcast|webinar|forum|trade_fair|other",
  "integration_required": "bool",
  "systems_mentioned": "string[]",
  "main_objection": "string|null",
  "competitors_mentioned": "string[]",
  "personalization_concern": "low|medium|high",
  "data_sensitivity": "low|medium|high",
  "close_probability": "float 0..1",
  "customer_segment": "smb|midmarket|enterprise|unknown",
  "key_topics": "string[]",
  "summary_es": "string (1-2 oraciones)"
}"""


SYSTEM_PROMPT = f"""Eres un analista experto en ventas B2B que categoriza transcripciones de reuniones comerciales.

CONTEXTO: Las transcripciones son monólogos en español del cliente, describiendo su empresa, sus dolores actuales y por qué les interesa Vambe (chatbot/automatización de atención al cliente).

TU TAREA: Devolver EXCLUSIVAMENTE un objeto JSON válido que cumpla el siguiente schema. No incluyas texto antes ni después del JSON. No uses code fences.

REGLAS:
- Todos los campos son obligatorios.
- Los valores de enums deben ser EXACTAMENTE uno de los listados, en minúsculas.
- `interest_level` es un entero entre 1 y 5.
- `sentiment` es un float entre -1.0 (muy negativo) y 1.0 (muy positivo).
- `close_probability` es un float entre 0.0 y 1.0.
- `summary_es` debe ser 1 o 2 oraciones en español.
- Si una dimensión no es deducible de la transcripción, usa el valor neutro razonable (`other`, `unknown`, listas vacías, `null` solo donde el schema lo permite).

SCHEMA:
{SCHEMA_SUMMARY}
"""


def build_user_prompt(transcript: str) -> str:
    return f"Categoriza la siguiente transcripción:\n\n{transcript}"
