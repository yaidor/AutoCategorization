# SalesCat

Categorización automática con LLM de transcripciones de reuniones de ventas B2B, expuesta como dashboard interactivo.

Pipeline: CSV → ingesta validada → LLM (Groq llama-3.3-70b por default) → dashboard con KPIs, charts, tabla de clientes con drawer de detalle, y re-categorización on-demand.

---

## Estado del proyecto: MVP

**Funcional, deployeado en producción** (Railway + Vercel). Cubre end-to-end los casos de uso del enunciado original.

### Lo que incluye

- ✅ **Ingesta CSV** con validación fila por fila, idempotencia por `transcript_hash`, upsert dinámico de sellers nuevos.
- ✅ **Categorización con LLM** vía Protocol pattern: `MockProvider` (determinístico, para tests) y `GroqProvider` (HTTP + JSON mode + retries con `tenacity` + semáforo de concurrencia + re-prompt en respuesta inválida).
- ✅ **Procesamiento batch** con `BackgroundTasks` + persistencia de jobs en Postgres + polling desde el frontend.
- ✅ **Dashboard de métricas** con 6 KPIs, 4 charts (close rate por vendedor, por industria, canales de descubrimiento, top objeciones) y filtros globales sincronizados a la URL.
- ✅ **Tabla de clientes** con TanStack Table (sort, paginación server-side), drawer de detalle con tabs (categorización, transcript, JSON crudo) y botón de re-categorizar con confirmación.
- ✅ **Auth** vía API key en header (`X-API-Key`) protegiendo todo `/api/v1/*`. Login en el frontend persiste la key en `localStorage`.
- ✅ **Theming** claro/oscuro con transición suave, sidebar responsive (collapse en mobile).
- ✅ **CI verde** (GitHub Actions): backend lint + type + 73 tests; frontend typecheck + lint + build.
- ✅ **Deploy a producción**: backend en Railway (Postgres + Redis + servicio FastAPI), frontend en Vercel.

### Lo que NO incluye (decisiones explícitas para acotar scope)

- ❌ **Login con usuarios reales** — un solo API key compartido.
- ❌ **Multi-tenant** — single org.
- ❌ **Worker queue real con `arq`** — `BackgroundTasks` de FastAPI alcanza para batches del orden de 60–500 meetings. La dep está instalada y Redis está levantado para sumarlo cuando crezca.
- ❌ **Rate limiting** en backend.
- ❌ **Code-splitting** del bundle frontend (~810 KB JS, 240 KB gzip — Recharts y TanStack Table son los gordos).
- ❌ **Sentry / observability más allá de `structlog`**.

Detalles de cómo se implementarían en la sección **Próximos pasos**.

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + Pydantic v2 + SQLAlchemy 2.0 async + asyncpg + Alembic + structlog |
| LLM | Groq llama-3.3-70b-versatile (default) — Protocol pattern para swap |
| DB / Cache | Postgres 16 + Redis 7 (Redis preparado para `arq`, no usado todavía) |
| Frontend | Vite + React 18 + TypeScript + Tailwind CSS v4 + shadcn/ui (Radix) |
| Data fetching | TanStack Query v5 + TanStack Table v8 + Recharts |
| Deploy | Railway (backend, Postgres, Redis) + Vercel (frontend) |
| CI | GitHub Actions (lint + typecheck + tests en cada push) |

---

## Quickstart local

Tiempo estimado: 10 minutos la primera vez.

### Pre-requisitos

- **Docker Desktop** (para Postgres + Redis)
- **Python 3.12 o superior**
- **Node 20 o superior** (incluye npm)
- **Git**

### 1. Clonar y levantar Postgres + Redis

```bash
git clone https://github.com/<tu-usuario>/AutoCategorization.git
cd AutoCategorization
docker compose up -d db redis
```

**Validación**:

```bash
docker ps
```

Deben aparecer `salescat-db` y `salescat-redis` en estado `healthy`.

### 2. Backend

```bash
cd backend
python -m venv .venv

# Activar venv:
# - Windows Git Bash:  source .venv/Scripts/activate
# - Windows PowerShell: .\.venv\Scripts\Activate.ps1
# - macOS / Linux:     source .venv/bin/activate

pip install -e ".[dev]"
```

Configurar variables de entorno:

```bash
cp .env.example .env
```

Editar `.env`:

- `SALESCAT_API_KEY=` — generar con `python -c "import secrets; print(secrets.token_urlsafe(32))"` y pegar el resultado. Sin esto, el gate de auth queda desactivado en dev.
- `SALESCAT_LLM_API_KEY=` — pegar tu key de Groq (https://console.groq.com/keys). Sin esto el provider real no funciona, pero puedes usar el `MockProvider` cambiando `SALESCAT_LLM_PROVIDER=mock`.

Aplicar migraciones y seed:

```bash
alembic upgrade head
python -m app.cli.seed
```

Levantar el server:

```bash
uvicorn app.main:app --reload --port 8000
```

**Validación**:

```bash
# Healthcheck público
curl http://localhost:8000/health
# → {"status":"ok"}

# Endpoint protegido sin key — debe rechazar
curl http://localhost:8000/api/v1/sellers
# → 401 + {"detail":"API key inválida o ausente"}

# Endpoint con key correcta — debe devolver los 5 sellers
curl http://localhost:8000/api/v1/sellers -H "X-API-Key: <tu-key>"
# → [{"id":1,"name":"Boa"},{"id":2,"name":"Puma"},...]
```

Documentación interactiva (Swagger): http://localhost:8000/docs

### 3. Frontend

En otra terminal:

```bash
cd frontend
npm install
cp .env.example .env   # apunta a http://localhost:8000 por default
npm run dev
```

**Validación**:

1. Abrir http://localhost:5173 → te redirige a `/login`.
2. Pegar la `SALESCAT_API_KEY` que generaste → click "Entrar".
3. Si ves el dashboard cargar con KPIs en 0, **el frontend está conectado al backend**.
4. Sidebar → "Carga CSV" → arrastrar `vambe_clients.csv` (untracked en la raíz del repo, son 60 transcripciones sintéticas) → "Cargar CSV". Debes ver `60 filas insertadas`.
5. Click "Categorizar reuniones nuevas" → arranca un job. El polling actualiza el progreso cada 2s.
6. **Nota**: Groq free tier tiene un límite de 1200 tokens/minuto que es estricto para 60 meetings. Es esperable que las primeras rondas fallen unas cuantas — el sistema captura los fallos y permite re-disparar el batch (cache filter solo procesa las pendientes). Suele tardar 3–4 rondas.
7. Cuando todas están categorizadas, ir al Dashboard → ver KPIs y charts con datos reales. Ir a "Clientes" → tabla con 60 filas, click en una → drawer con detalle, transcript, categorización completa.

### 4. Tests + checks

Backend:

```bash
cd backend
ruff check .
ruff format --check .
mypy app
pytest
# 73 tests passing
```

Frontend:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

---

## Estructura del repo

```
.
├── backend/                         # FastAPI service
│   ├── app/
│   │   ├── api/v1/                  # routers: customers, meetings, jobs, metrics, sellers, uploads
│   │   ├── core/                    # config, logging, middleware (request-id), security (API key gate)
│   │   ├── db/                      # async engine + session factory
│   │   ├── models/                  # SQLAlchemy 2.0 typed (Seller, Customer, Meeting, Categorization, Job)
│   │   ├── schemas/                 # Pydantic DTOs (request/response)
│   │   ├── services/
│   │   │   ├── csv_ingest.py        # parse + persist con idempotencia
│   │   │   ├── customers.py         # listado paginado + detalle
│   │   │   ├── metrics.py           # 5 agregaciones con filtros compartidos
│   │   │   ├── categorization/      # service + batch + mapping LLM → DB
│   │   │   └── llm/                 # Protocol provider + Groq + Mock + prompt + schema
│   │   └── cli/seed.py              # idempotente, los 5 sellers canónicos
│   ├── alembic/                     # migraciones (initial_schema + add_jobs_table)
│   ├── tests/                       # 73 tests (parser, schema, mapping, providers con httpx mock, etc.)
│   ├── Dockerfile                   # production-ready
│   └── railway.json                 # config de deploy (preDeployCommand + healthcheck)
│
├── frontend/                        # Vite + React app
│   ├── src/
│   │   ├── api/                     # client + types + fetchers (customers, metrics, uploads)
│   │   ├── auth/                    # AuthContext + RequireAuth guard
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn primitives
│   │   │   ├── layout/              # AppShell + Sidebar + Topbar
│   │   │   ├── filters/             # GlobalFilters (URL params como source of truth)
│   │   │   ├── charts/              # 4 charts del dashboard
│   │   │   ├── customers/           # tabla + drawer + categorization view + recategorize button
│   │   │   └── upload/              # dropzone + summary + job progress
│   │   ├── pages/                   # Login, Dashboard, Customers, CustomerDetail, Upload
│   │   ├── hooks/useMetricsFilters.ts
│   │   └── lib/                     # format, labels (humanize enums), query-client
│   └── eslint.config.js, vite.config.ts, ...
│
├── docs/
│   └── deploy.md                    # guía paso a paso de deploy con sección de troubleshooting
│
├── docker-compose.yml               # Postgres + Redis + (opcional) backend + frontend
├── Makefile                         # db-upgrade, db-reset, db-seed
└── README.md                        # este archivo
```

---

## Decisiones y supuestos

Decisiones tomadas durante el desarrollo, con su justificación:

### Arquitectura

- **Mono-repo split-ready**: `backend/` y `frontend/` son autocontenidos (cada uno con su `Dockerfile`, `package.json`, tests). El contrato API cambia mucho al inicio; cuando se estabilice, dividir con `git subtree split` es operación de un solo comando.
- **Backend: FastAPI + SQLAlchemy 2.0 async + Pydantic v2**. Estándar moderno, tipos typed end-to-end, OpenAPI auto-generado, async nativo.
- **Frontend: Vite + React + Tailwind v4 + shadcn/ui**. Bundle liviano (sin SSR overkill), tipado strict TS, theming via CSS variables compatible con dark mode.

### LLM

- **Protocol pattern para providers** (`app/services/llm/base.py`): el `LLMProvider` Protocol define el contrato `categorize(transcript) -> LLMResponse`. Hay implementaciones para Mock (determinístico, seed = sha256 del transcript) y Groq (httpx + tenacity + semáforo). Sumar Anthropic, OpenAI o Gemini son ~80 líneas de código + 1 línea en `factory.py`.
- **Groq como default**: `llama-3.3-70b-versatile` con JSON mode. Free tier real (1200 TPM), bueno para iterar sin gasto. Para producción seria conviene tier paid o sumar Anthropic como fallback.
- **Cache por unique constraint**: `(meeting_id, prompt_version, model)` en la tabla `categorizations`. Re-disparar batch solo procesa las que faltan. Cambiar el prompt (bump `PROMPT_VERSION` en `app/services/llm/prompt.py`) invalida el cache automáticamente — la nueva categorización convive con la vieja hasta que se haga `force=true` (que borra la previa).
- **Re-prompt en respuesta inválida**: si el LLM devuelve JSON malformado o que no cumple el schema Pydantic, el provider re-llama una vez con feedback del error en el user prompt.

### Auth

- **API key compartida** en header `X-API-Key`, en lugar de JWT con users reales. Decisión consciente para el alcance MVP/assessment: demuestra el principio de protección sin la complejidad de gestión de usuarios. Upgrade a JWT real es trabajo aislado documentado en *Próximos pasos*.
- **Public endpoints**: `/`, `/health`, `/version`, `/docs`, `/openapi.json`. Lockeado: todo `/api/v1/*`. Razón: Railway/Kubernetes hacen healthcheck público; Swagger UI ofrece discoverability sin acceso a datos.
- **API key se valida con probe en login**: el frontend hace `GET /api/v1/metrics/overview` con la key tipeada antes de guardarla en `localStorage`. Si responde 401, muestra error en vez de aceptar credenciales malas.

### Procesamiento

- **Single-meeting categorize**: síncrono, request bloqueante hasta que el LLM devuelve.
- **Batch categorize**: dispara `BackgroundTasks`, devuelve `job_id` inmediato, frontend pollea `GET /jobs/{id}` cada 2s. Cuando crezca por encima de ~500 meetings, conviene migrar a `arq` worker (la dep ya está + Redis levantado).
- **Idempotencia por `transcript_hash` (SHA256)**: re-subir el mismo CSV no duplica meetings. Re-disparar batch-categorize procesa solo las pendientes.
- **Pre-deploy migrations**: `alembic upgrade head && python -m app.cli.seed` corre como `preDeployCommand` en Railway (container efímero), no como parte del start command. Esto previene el bug clásico de "seed cuelga → uvicorn nunca arranca → healthcheck falla".

### Datos

- **`closed` viene del CSV** y es independiente del `close_probability` predicho por el LLM. Mantenemos ambos para análisis (calibración del LLM = comparar predicción vs realidad).
- **Enums Postgres**: `industry`, `use_case`, `urgency`, `discovery_channel`, `personalization_concern`, `data_sensitivity`, `customer_segment`, `volume_period`. Garantiza integridad y permite queries directas. SQLAlchemy serializa los `value` (lowercase) y no los `name` (necesita `values_callable`).
- **Customer dedup por `(name, seller_id)`**: el mismo nombre con dos vendedores se trata como dos relaciones comerciales (defensible para B2B).

### Frontend

- **URL como source of truth de filtros**: dashboard, customers list, drawer abierto — todo en `useSearchParams`. URLs compartibles vía link, persistencia automática al recargar.
- **TanStack Query como cache**: cada widget hace su propio `useQuery({ queryKey: [...filters] })`. Cambiar un filtro refetchea solo lo que cambió.
- **Tipos manuales en `src/api/types.ts`**: el script `npm run gen:api` genera tipos desde el OpenAPI del backend, pero el bootstrap inicial fue manual para no acoplar el frontend a un backend en evolución. Refactor a tipos generados es cambio mecánico.
- **Tailwind v4 + shadcn/ui v4**: usa CSS variables (`--color-background`, etc.) y `@theme inline` en lugar del config JS de v3. Custom variants declaradas en `index.css` para los `data-state` de Radix.

### UI / UX

- **Español neutro/chileno** en todas las strings (sin voseo argentino).
- **Theme toggle claro/oscuro** con transición de 200ms; `next-themes` para persistencia + system detection.
- **Sidebar responsive**: fija en desktop (≥768px), colapsable con hamburger en mobile.
- **Confirmación destructiva**: re-categorizar (que borra la categorización anterior) requiere modal de confirmación. Acciones idempotentes (cargar CSV, dispar batch) no.

---

## Por qué es escalable

El MVP está dimensionado para 60–1000 meetings. La arquitectura sostiene el crecimiento sin reescribir:

### Backend

- **SQLAlchemy async + Postgres** maneja >100k meetings sin tocar código. Índices ya creados: `(seller_id, meeting_date)` compuesto, `closed`, `industry` (B-tree), `key_topics` con GIN para búsqueda en arrays.
- **Provider pattern para LLM**: agregar Anthropic como fallback de Groq es ~80 líneas (1 archivo nuevo + 1 línea en factory). Permite distribuir carga entre providers o degradar gracefully ante rate limits.
- **Cache por unique constraint**: cambiar el prompt invalida selectivamente sin perder data histórica. Re-correr el LLM con otro prompt o modelo no destruye categorizaciones previas (cada `(meeting_id, prompt_version, model)` es una fila distinta).
- **`jobs` table**: el estado de batches vive en Postgres, no en memoria. Multi-worker es cuestión de sumar `arq` consumiendo de la misma tabla — sin race conditions, sin redesign.
- **Migraciones Alembic**: schema evoluciona sin downtime, todos los cambios son reversibles. Las migraciones tienen naming conventions explícitas (`pk_*`, `fk_*`, `uq_*`, `ix_*`) para que las generaciones futuras sean predecibles.
- **structlog con `request_id` middleware**: cada request tiene un ID que se propaga vía contextvar a todos los logs. Conectar a Datadog / Honeycomb / Sentry es un solo procesador adicional en `core/logging.py`.

### Frontend

- **TanStack Query**: invalidación granular por `queryKey`. Servidor escalado no requiere cambios en cliente.
- **URL params como state**: zero overhead de state management, comparte estado entre tabs/usuarios sin sesiones server-side.
- **Component splitting**: los charts y la tabla pueden volverse `lazy()` + `Suspense` cuando se haga code-splitting (1 hora de trabajo cuando el bundle moleste).

### Operaciones

- **Healthcheck público + auth gate**: Railway / Kubernetes balancean sin acceder a datos.
- **Deploy declarativo**: `Dockerfile`, `railway.json`, y el setup de Vercel viven en el repo. Reproducir el deploy completo desde cero toma ~30 minutos siguiendo `docs/deploy.md`.
- **CI gate**: lint + typecheck + tests corren en cada push a `main`. CI rojo bloquea deploys.

---

## Próximos pasos

En orden de prioridad:

1. **JWT auth real** — agregar tabla `users`, endpoint `/auth/login` con bcrypt, JWT issuance, refresh tokens. Trabajo aislado: ~300 líneas backend + reemplazar el form de API key por user/password en el frontend.
2. **Rate limiting** con `slowapi` (FastAPI middleware sobre `limits`). Importante antes de exponer públicamente sin auth fuerte.
3. **Tests de integración con Postgres en CI** — agregar Postgres como service en GitHub Actions, levantar tests que tocan DB (los tests actuales son puros para que CI pase sin DB).
4. **Worker queue con `arq`** — cuando los batches superen ~500 meetings o se quiera retry automático.
5. **Multi-provider LLM con fallback** — Groq como primario, Anthropic como fallback. Implementación: un `FallbackProvider` que envuelve dos providers y reintenta con el segundo si el primero hace rate-limit.
6. **Sentry** para errores no capturados en backend y frontend.
7. **Code-splitting del bundle frontend** — `lazy()` + `Suspense` para Recharts y TanStack Table. Bundle inicial bajaría de ~810 KB a ~250 KB.
8. **Charts adicionales** — tendencia temporal de meetings, top systems mentioned, top competitors mentioned, distribución de close_probability, customer_segment × seller, matriz urgencia × close_probability.

---

## Documentación adicional

- [`docs/deploy.md`](./docs/deploy.md) — guía paso a paso de deploy a Railway + Vercel, con sección de troubleshooting cubriendo los gotchas que descubrimos en el camino.
- [`backend/README.md`](./backend/README.md) — comandos backend, estructura interna, scripts útiles.
- [`frontend/README.md`](./frontend/README.md) — comandos frontend, estructura interna.

## Licencia

Privado. Todos los derechos reservados.
