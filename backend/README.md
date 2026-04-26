# salescat-api

Backend FastAPI de SalesCat. Categoriza transcripciones de reuniones de ventas usando un LLM (Groq por default), expone metrics y customers vía REST con auth por API key.

Para el quickstart end-to-end (incluyendo frontend), ver el [README raíz](../README.md).

## Setup local rápido

Desde la raíz del repo, levantar Postgres + Redis con Docker:

```bash
docker compose up -d db redis
```

En este directorio (`backend/`):

```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash
# o: source .venv/bin/activate     # macOS/Linux
# o: .\.venv\Scripts\Activate.ps1  # Windows PowerShell

pip install -e ".[dev]"

cp .env.example .env
# Editar .env: setear SALESCAT_API_KEY (random) y SALESCAT_LLM_API_KEY (Groq).
# Para usar el provider Mock sin Groq: SALESCAT_LLM_PROVIDER=mock

alembic upgrade head
python -m app.cli.seed
uvicorn app.main:app --reload
```

Verificación:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}

curl http://localhost:8000/api/v1/sellers -H "X-API-Key: <tu-key>"
# → 5 sellers
```

Swagger UI: http://localhost:8000/docs

## Tests, lint, format, types

```bash
pytest                # 73 tests
ruff check .          # lint
ruff format --check . # format check
mypy app              # type check
```

## Migraciones (Alembic)

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Generar nueva migración (autogenerate desde los modelos)
alembic revision --autogenerate -m "descripción"

# Bajar una versión (rollback)
alembic downgrade -1
```

> **Nota**: el autogenerate de Alembic NO incluye `DROP TYPE` para enums Postgres. Si la migración crea tipos enum (e.g., `industry`, `urgency`), hay que agregar manualmente al `downgrade()`:
>
> ```python
> for enum_name in ("industry", "urgency", ...):
>     op.execute(f"DROP TYPE IF EXISTS {enum_name}")
> ```

Desde la raíz del repo hay un `Makefile` con shortcuts:

```bash
make db-upgrade    # alembic upgrade head
make db-downgrade  # alembic downgrade -1
make db-reset      # downgrade base + upgrade head + seed
make db-seed       # python -m app.cli.seed
```

## Estructura

```
app/
├── api/v1/
│   ├── __init__.py             # router agregador con prefix /api/v1 + dependency verify_api_key
│   ├── customers.py            # GET /customers (paginado), GET /customers/{id}
│   ├── jobs.py                 # GET /jobs/{id}
│   ├── meetings.py             # POST /meetings/{id}/categorize, POST /meetings/batch-categorize
│   ├── metrics.py              # GET /metrics/{overview|by-seller|by-industry|objections|discovery-channels}
│   ├── sellers.py              # GET /sellers
│   └── uploads.py              # POST /uploads/csv (multipart)
│
├── api/health.py               # GET /health, GET /version (públicos, fuera del v1 gate)
│
├── core/
│   ├── config.py               # Settings con pydantic-settings (env_prefix=SALESCAT_)
│   ├── logging.py              # structlog + ProcessorFormatter integrado con stdlib logging
│   ├── middleware.py           # RequestIDMiddleware (genera/respeta X-Request-ID, log por request)
│   └── security.py             # verify_api_key dependency
│
├── db/
│   ├── base.py                 # DeclarativeBase con naming conventions
│   └── session.py              # async engine + async_session_factory + get_session dependency
│
├── models/
│   ├── enums.py                # 8 StrEnums (Industry, UseCase, ...)
│   ├── seller.py, customer.py, meeting.py, categorization.py, job.py
│   └── __init__.py             # re-exports para Alembic detection
│
├── schemas/
│   ├── ingest.py               # MeetingRow, IngestError, IngestSummary
│   ├── customers.py            # CustomerListItem, CustomerDetailResponse, ...
│   ├── categorization.py       # CategorizationResponse, JobResponse
│   └── metrics.py              # OverviewResponse, SellerMetric, IndustryMetric, ...
│
├── services/
│   ├── csv_ingest.py           # parse_csv_bytes (puro) + persist_rows + ingest_csv
│   ├── customers.py            # list_customers, get_customer_detail
│   ├── metrics.py              # 5 fetchers + MetricsFilters dataclass + _apply_filters helper
│   ├── categorization/
│   │   ├── service.py          # categorize_meeting (single, sync)
│   │   ├── batch.py            # create_batch_job + run_batch_job (BackgroundTasks)
│   │   └── mapping.py          # build_categorization (LLMResponse → SQLAlchemy Categorization)
│   └── llm/
│       ├── base.py             # LLMProvider Protocol + LLMResponse + 4 excepciones
│       ├── schema.py           # CategorizationResult Pydantic (validación de output del LLM)
│       ├── prompt.py           # SYSTEM_PROMPT, SCHEMA_SUMMARY, build_user_prompt, PROMPT_VERSION
│       ├── factory.py          # get_llm_provider() según settings.llm_provider
│       └── providers/
│           ├── mock.py         # MockProvider (determinístico)
│           └── groq.py         # GroqProvider (httpx + tenacity + semáforo + re-prompt)
│
├── cli/
│   └── seed.py                 # idempotente, los 5 sellers canónicos
│
└── main.py                     # create_app(): FastAPI factory + CORS + lifespan + middleware

alembic/                        # migraciones (env.py async)
tests/                          # pytest, 73 tests
Dockerfile                      # production-ready (sh -c con $PORT fallback)
railway.json                    # config Railway (preDeployCommand + healthcheck)
pyproject.toml                  # deps + tool config (ruff, mypy, pytest)
```

## Variables de entorno

Todas con prefijo `SALESCAT_`. Listado completo en `.env.example`.

| Variable | Default | Descripción |
|---|---|---|
| `SALESCAT_ENVIRONMENT` | `development` | `development` / `production` |
| `SALESCAT_LOG_LEVEL` | `INFO` | Nivel de structlog |
| `SALESCAT_DATABASE_URL` | `postgresql+asyncpg://...localhost...` | Acepta también `postgresql://` (Railway) — se autoconvierte |
| `SALESCAT_REDIS_URL` | `redis://localhost:6379/0` | Para `arq` cuando se sume |
| `SALESCAT_CORS_ORIGINS` | `http://localhost:5173` | Lista separada por coma |
| `SALESCAT_LLM_PROVIDER` | `mock` | `mock` o `groq` |
| `SALESCAT_LLM_MODEL` | (vacío → default por provider) | Para Groq: `llama-3.3-70b-versatile` |
| `SALESCAT_LLM_API_KEY` | (vacío) | Solo para Groq |
| `SALESCAT_LLM_TIMEOUT_SECONDS` | `30` | Por request al LLM |
| `SALESCAT_LLM_MAX_CONCURRENT` | `5` | Semáforo dentro del provider |
| `SALESCAT_API_KEY` | (vacío) | Si vacía → auth deshabilitada (warning al startup). Si seteada → header `X-API-Key` requerido en `/api/v1/*` |

## Endpoints principales

Públicos (sin API key):

- `GET /` — service info
- `GET /health` — `{"status":"ok"}`
- `GET /version` — `{"version", "environment"}`
- `GET /docs`, `/openapi.json` — Swagger

Protegidos (header `X-API-Key`):

- `POST /api/v1/uploads/csv` — multipart, ingesta de CSV
- `POST /api/v1/meetings/{id}/categorize?force=` — single, síncrono
- `POST /api/v1/meetings/batch-categorize?force=` — background job
- `GET /api/v1/jobs/{id}` — status del job
- `GET /api/v1/customers?...` — paginado con sort + filtros
- `GET /api/v1/customers/{id}` — detalle con categorizaciones
- `GET /api/v1/sellers` — lista para dropdown
- `GET /api/v1/metrics/{overview|by-seller|by-industry|objections|discovery-channels}` — agregaciones con filtros compartidos

Filtros compartidos en `/customers` y `/metrics/*`: `?from=&to=&seller_id=&industry=&closed=&uncategorized=`. En customers también `?search=` y `?skip=&limit=&sort=`.
