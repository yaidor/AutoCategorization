.PHONY: db-upgrade db-downgrade db-reset db-seed db-revision

# Comandos asumen que estás dentro del venv del backend.
# Uso típico:
#   cd backend && source .venv/Scripts/activate && make -C .. db-upgrade

db-upgrade:
	cd backend && alembic upgrade head

db-downgrade:
	cd backend && alembic downgrade -1

db-reset:
	cd backend && alembic downgrade base && alembic upgrade head && python -m app.cli.seed

db-seed:
	cd backend && python -m app.cli.seed

db-revision:
	cd backend && alembic revision --autogenerate -m "$(MSG)"
