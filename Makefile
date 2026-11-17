.PHONY: dev dev-down worker worker-llm test test-api test-worker-scrapper test-worker-llm test-frontend

dev:
	docker compose up -d --wait postgres
	docker compose up -d --no-deps api
	cd frontend && ([ -d node_modules ] || bun install) && bun run dev -- --port 5173

dev-down:
	docker compose stop api postgres

worker:
	# Limita a concorrência ao número de CPUs disponíveis (ou ajuste para metade, se preferir)
	uv run celery -A pje_scraper.worker worker --loglevel=INFO --concurrency=$$(nproc)

worker-llm:
	cd apps/worker-llm && uv run celery -A worker worker --loglevel=INFO --concurrency=$$(nproc)

test-api:
	cd apps/api && uv run pytest

test-worker-scrapper:
	cd apps/worker-scrapper && uv run pytest

test-worker-llm:
	cd apps/worker-llm && uv run pytest

test: test-api test-worker-scrapper test-worker-llm
