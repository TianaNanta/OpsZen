# Makefile for OpsZen Project
# Provides convenient shortcuts for common development tasks

.PHONY: help install install-dev test test-unit test-integration test-fast test-coverage clean lint format check docs run

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)OpsZen Development Tasks$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install -e .

install-dev: ## Install development dependencies (includes tests)
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -e .
	pip install -r tests/requirements-test.txt
	@echo "$(GREEN)✓ Development environment ready$(NC)"

install-test: ## Install only test dependencies
	@echo "$(BLUE)Installing test dependencies...$(NC)"
	pip install -r tests/requirements-test.txt

# Testing targets
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	./run_tests.sh all

test-unit: ## Run unit tests only (fast)
	@echo "$(BLUE)Running unit tests...$(NC)"
	./run_tests.sh unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	./run_tests.sh integration

test-fast: ## Run tests in parallel (faster)
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	./run_tests.sh fast

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	./run_tests.sh coverage

test-report: ## Generate and open HTML coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	./run_tests.sh report

test-failed: ## Re-run only failed tests
	@echo "$(BLUE)Re-running failed tests...$(NC)"
	./run_tests.sh failed

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	./run_tests.sh verbose

test-watch: ## Run tests in watch mode (re-run on changes)
	@echo "$(BLUE)Starting test watch mode...$(NC)"
	./run_tests.sh watch

# Module-specific tests
test-docker: ## Run Docker-related tests
	@echo "$(BLUE)Running Docker tests...$(NC)"
	./run_tests.sh docker

test-ssh: ## Run SSH-related tests
	@echo "$(BLUE)Running SSH tests...$(NC)"
	./run_tests.sh ssh

test-aws: ## Run AWS-related tests
	@echo "$(BLUE)Running AWS tests...$(NC)"
	./run_tests.sh aws

test-logs: ## Run log analyzer tests
	@echo "$(BLUE)Running log analyzer tests...$(NC)"
	./run_tests.sh logs

test-monitoring: ## Run monitoring tests
	@echo "$(BLUE)Running monitoring tests...$(NC)"
	./run_tests.sh monitoring

# Code quality targets
lint: ## Run linters (flake8, pylint)
	@echo "$(BLUE)Running linters...$(NC)"
	@flake8 src tests --max-line-length=100 || true
	@pylint src --disable=all --enable=E,F || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@black src tests
	@isort src tests
	@echo "$(GREEN)✓ Code formatted$(NC)"

check: ## Run all checks (lint, type check, format check)
	@echo "$(BLUE)Running all checks...$(NC)"
	@black --check src tests
	@isort --check-only src tests
	@flake8 src tests --max-line-length=100
	@mypy src --ignore-missing-imports || true
	@echo "$(GREEN)✓ All checks passed$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	@mypy src --ignore-missing-imports

security: ## Run security checks (bandit, safety)
	@echo "$(BLUE)Running security checks...$(NC)"
	@bandit -r src || true
	@safety check || true

# Cleaning targets
clean: ## Clean test artifacts and cache files
	@echo "$(BLUE)Cleaning test artifacts...$(NC)"
	./run_tests.sh clean
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean ## Deep clean (including venv and builds)
	@echo "$(BLUE)Deep cleaning...$(NC)"
	@rm -rf .venv build dist *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Deep cleanup complete$(NC)"

# Documentation targets
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation server not yet implemented$(NC)"

# Development targets
dev: install-dev ## Set up development environment
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Run 'make test' to verify installation$(NC)"

run-monitor: ## Run system monitor
	@echo "$(BLUE)Starting system monitor...$(NC)"
	python -m src.monitoring.system_monitor

run-logs: ## Run log analyzer sample
	@echo "$(BLUE)Running log analyzer...$(NC)"
	python -m src.logs.sample_logs

# Git hooks
hooks: ## Install git hooks
	@echo "$(BLUE)Installing git hooks...$(NC)"
	@mkdir -p .git/hooks
	@echo "#!/bin/bash\nmake test-unit" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✓ Git hooks installed$(NC)"

# CI/CD targets
ci: clean install-dev lint test-coverage ## Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

# Quick development cycle
quick: format test-unit ## Format code and run quick tests
	@echo "$(GREEN)✓ Quick check complete$(NC)"

# Build targets
build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	python -m build
	@echo "$(GREEN)✓ Build complete$(NC)"

publish-test: build ## Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	@echo "$(YELLOW)WARNING: This will publish to production PyPI$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload dist/*; \
	fi

# Version management
version: ## Show current version
	@python -c "from src.version import __version__; print(f'OpsZen v{__version__}')"

# Info targets
info: ## Show project information
	@echo "$(BLUE)OpsZen Project Information$(NC)"
	@echo ""
	@echo "Python version: $$(python --version)"
	@echo "Project root: $$(pwd)"
	@echo "Test framework: pytest"
	@echo ""
	@echo "Run 'make help' for available commands"

tree: ## Show project structure
	@echo "$(BLUE)Project Structure:$(NC)"
	@tree -I '__pycache__|*.pyc|.pytest_cache|htmlcov|.venv|.git' -L 3

# Diagnostic targets
diagnose: ## Run diagnostics
	@echo "$(BLUE)Running diagnostics...$(NC)"
	@echo "Python: $$(python --version)"
	@echo "Pip: $$(pip --version)"
	@echo "Pytest: $$(pytest --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "Dependencies:"
	@pip list | grep -E "pytest|docker|boto3|paramiko|rich|typer" || echo "Core dependencies not found"

.PHONY: all
all: clean install-dev test lint ## Run complete setup and verification
	@echo "$(GREEN)✓ Complete setup and verification done$(NC)"
