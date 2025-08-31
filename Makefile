.PHONY: help install test lint format type-check check build clean dev-install pre-commit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev-install: ## Install development dependencies
	uv sync --dev

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src/ingest_pdf --cov-report=term-missing --cov-report=html

test-verbose: ## Run tests in verbose mode
	uv run pytest -v

lint: ## Run linting
	uv run ruff check .

lint-fix: ## Run linting with auto-fix
	uv run ruff check --fix .

format: ## Format code
	uv run black .

format-check: ## Check code formatting
	uv run black --check .

type-check: ## Run type checking
	uv run mypy src/

check: ## Run all quality checks
	uv run ruff check .
	uv run black --check .
	uv run mypy src/
	uv run pytest

pre-commit: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

build: ## Build the package
	uv build

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dev-setup: dev-install pre-commit ## Set up development environment
	@echo "Development environment setup complete!"

run-example: ## Run example CLI commands (requires sample PDFs)
	@echo "Example CLI commands:"
	@echo "  ingest-pdf --help"
	@echo "  ingest-pdf process sample.pdf"
	@echo "  ingest-pdf batch ./pdfs/"
	@echo "  ingest-pdf info sample.pdf"

# Development helpers
install-local: ## Install package in development mode
	uv pip install -e .

uninstall: ## Uninstall the package
	uv pip uninstall ingest-pdf

# Testing helpers
test-unit: ## Run only unit tests
	uv run pytest -m "unit"

test-integration: ## Run only integration tests  
	uv run pytest -m "integration"

test-fast: ## Run tests without slow tests
	uv run pytest -m "not slow"

# Security
security-check: ## Run security checks
	uv pip install safety bandit
	uv run safety check
	uv run bandit -r src/

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

# Docker helpers (for future use)
docker-build: ## Build Docker image
	@echo "Docker build not yet implemented"

docker-run: ## Run Docker container
	@echo "Docker run not yet implemented"