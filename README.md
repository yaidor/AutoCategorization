# SalesCat

Ingesta y categorización automática de reuniones de ventas B2B con LLM, servida como dashboard interactivo.

## Estructura

- [`backend/`](./backend) — API FastAPI + Postgres + Alembic. Split-ready para mover a su propio repo.
- [`frontend/`](./frontend) — Dashboard React + TypeScript + Tailwind. Split-ready.
- [`docs/`](./docs) — Guías de deploy, prompt del LLM y definición de métricas.
- [`docker-compose.yml`](./docker-compose.yml) — Entorno de desarrollo local.

## Requisitos

- Docker Desktop
- Python 3.12+
- Node 20+

## Quickstart (desarrollo local)

```bash
# Levantar Postgres + Redis + backend en contenedores
docker compose up -d db redis backend

# Frontend (local, recomendado para iterar)
cd frontend
npm install
npm run dev
```

- Backend: http://localhost:8000 — docs interactivas en `/docs`
- Frontend: http://localhost:5173

Alternativamente, `docker compose up` levanta los 4 servicios (incluye frontend containerizado).

## Comandos útiles

Backend (en `backend/`, con venv o dentro del contenedor):

```bash
pytest                 # tests
ruff check . --fix     # lint + autofix
ruff format .          # formateo
mypy app               # tipos
alembic upgrade head   # aplicar migraciones (cuando existan)
```

Frontend (en `frontend/`):

```bash
npm run dev            # servidor de desarrollo
npm run lint           # eslint
npm run typecheck      # tsc --noEmit
npm run build          # build de producción
npm run format         # prettier --write
```

## Despliegue

Guía paso a paso en [`docs/deploy.md`](./docs/deploy.md).
Resumen: backend en **Railway** (FastAPI + Postgres + Redis), frontend en **Vercel**.
