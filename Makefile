.PHONY: install run test lint fmt typecheck migrate migration seed
install:    ; pip install -e ".[dev]"
run:        ; uvicorn app.main:app --reload
test:       ; pytest --cov=app --cov-report=term-missing
lint:       ; ruff check .
fmt:        ; ruff format . && ruff check . --fix
typecheck:  ; mypy app
migrate:    ; alembic upgrade head
migration:  ; alembic revision --autogenerate -m "$(m)"
seed:       ; python -m scripts.seed --admin-password "$(pw)" --students $(or $(n),0)
