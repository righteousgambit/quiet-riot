.PHONY: help install install-dev lint format test clean pre-commit-install pre-commit-run

help: ## Show this help message
	@echo "Quiet Riot Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	pip install -e .

install-dev: ## Install package with development dependencies
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run ruff linter
	ruff check .

format: ## Format code with ruff
	ruff format .

lint-fix: ## Fix linting issues automatically
	ruff check . --fix

type-check: ## Run mypy type checking
	mypy quiet_riot

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=quiet_riot --cov-report=html --cov-report=term

clean: ## Clean build artifacts and cache
	rm -rf build/ dist/ *.egg-info .eggs/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

all: clean install-dev lint type-check test ## Run all checks
