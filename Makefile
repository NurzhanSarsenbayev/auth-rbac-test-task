.PHONY: up down reset build migrate seed lint fix test demo demo-prepare demo-run logs shell

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up --build -d

build:
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

demo-prepare: reset migrate seed
	@echo "Demo environment has been reset and prepared."
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "Run 'make demo-run' to execute the demo scenario."

demo-run:
	app/scripts/demo.sh

demo: reset migrate seed
	@echo "Running end-to-end demo scenario..."
	@app/scripts/demo.sh
	@echo "Swagger UI: http://localhost:8000/docs"

logs:
	docker compose logs -f

shell:
	docker compose exec app bash