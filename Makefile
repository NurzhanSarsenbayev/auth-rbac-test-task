.PHONY: up down rebuild migrate seed lint test demo logs shell

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v

rebuild:
	docker compose up --build -d

migrate:
	docker compose exec app alembic upgrade head

seed:
	docker compose exec app python -m app.scripts.seed

lint:
	docker compose exec app ruff check .

fix:
	docker compose exec app ruff check . --fix && docker compose exec app ruff check .

test:
	docker compose exec app pytest

demo: rebuild migrate seed
	@echo "Demo is ready."
	@echo "Swagger UI: http://localhost:8000/docs"

logs:
	docker compose logs -f

shell:
	docker compose exec app bash