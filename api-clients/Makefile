.PHONY: help install dev test lint format clean docker-up docker-down migrate seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linter
	flake8 app
	mypy app

format: ## Format code
	black app tests
	isort app tests

clean: ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-build: ## Build Docker image
	docker-compose build

docker-logs: ## Show Docker logs
	docker-compose logs -f

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration
	alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback last migration
	alembic downgrade -1

seed: ## Seed database with test data
	python scripts/seed_data.py

init-db: ## Initialize database
	python scripts/init_db.py

run: ## Run the application
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-prod: ## Run the application in production mode
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
