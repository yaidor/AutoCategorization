# salescat-api

Backend FastAPI de SalesCat.

## Setup local (sin Docker)

```bash
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Health check: http://localhost:8000/

## Setup con Docker

Desde la raíz del repo:

```bash
docker compose up -d db redis backend
```

## Tests

```bash
pytest
```

## Lint & format

```bash
ruff check . --fix
ruff format .
mypy app
```

## Estructura

```
app/
  api/v1/          # routers HTTP
  core/            # config, logging, exceptions
  db/              # engine, session, seeds
  models/          # SQLAlchemy ORM
  schemas/         # Pydantic DTOs
  services/        # lógica de dominio (CSV, LLM, métricas)
  workers/         # jobs async con arq
  main.py          # entrypoint FastAPI
alembic/           # migraciones
tests/
```
