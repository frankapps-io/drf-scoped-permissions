.PHONY: help install install-dev test test-cov lint format clean build publish-test publish docs venv

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv
VENV_BIN := $(VENV)/bin
PACKAGE := drf_scoped_permissions

# Default target
help:
	@echo "DRF Scoped Permissions - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv          Create virtual environment"
	@echo "  make install       Install package in editable mode"
	@echo "  make install-dev   Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make lint          Run all linting checks"
	@echo "  make format        Format code with black and isort"
	@echo "  make typecheck     Run mypy type checking"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  make clean         Remove build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make publish-test  Publish to TestPyPI"
	@echo "  make publish       Publish to PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell         Open Django shell with package loaded"
	@echo "  make migrate       Run migrations (for testing)"
	@echo "  make list-scopes   List all discovered scopes"

# Setup targets
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at ./$(VENV)"
	@echo "Activate with: source $(VENV_BIN)/activate"

install:
	@echo "Installing package in editable mode..."
	$(PIP) install -e .

install-dev: venv
	@echo "Installing package with dev dependencies..."
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -e ".[dev]"
	@echo ""
	@echo "✅ Development environment ready!"
	@echo "Activate with: source $(VENV_BIN)/activate"

# Testing targets
test:
	@echo "Running tests..."
	pytest

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=$(PACKAGE) --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "✅ Coverage report generated in htmlcov/index.html"

test-verbose:
	@echo "Running tests in verbose mode..."
	pytest -vv

test-watch:
	@echo "Running tests in watch mode..."
	pytest-watch

# Code quality targets
lint: lint-ruff lint-mypy
	@echo ""
	@echo "✅ All linting checks passed!"

lint-ruff:
	@echo "Checking code with ruff..."
	ruff check $(PACKAGE) tests

lint-mypy:
	@echo "Type checking with mypy..."
	mypy $(PACKAGE)

format:
	@echo "Formatting code with ruff..."
	ruff check --fix $(PACKAGE) tests
	ruff format $(PACKAGE) tests
	@echo "✅ Code formatted!"

typecheck:
	@echo "Running type checks..."
	mypy $(PACKAGE)

# Building targets
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Build artifacts cleaned!"

build: clean
	@echo "Building distribution packages..."
	$(PYTHON) -m build
	@echo "✅ Packages built in dist/"
	@ls -lh dist/

# Publishing targets
publish-test: build
	@echo "Publishing to TestPyPI..."
	@echo "⚠️  Make sure you have a TestPyPI account and token configured"
	twine upload --repository testpypi dist/*
	@echo ""
	@echo "✅ Published to TestPyPI!"
	@echo "Test installation with:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ drf-scoped-permissions"

publish: build
	@echo "Publishing to PyPI..."
	@echo "⚠️  This will publish to the REAL PyPI. Are you sure? [Ctrl+C to cancel]"
	@read -p "Press Enter to continue..."
	twine upload dist/*
	@echo ""
	@echo "✅ Published to PyPI!"
	@echo "Install with: pip install drf-scoped-permissions"

# Django utilities (for testing)
shell:
	@echo "Opening Django shell..."
	DJANGO_SETTINGS_MODULE=tests.settings $(PYTHON) manage.py shell

migrate:
	@echo "Running migrations..."
	DJANGO_SETTINGS_MODULE=tests.settings $(PYTHON) manage.py migrate

list-scopes:
	@echo "Listing all discovered scopes..."
	DJANGO_SETTINGS_MODULE=tests.settings $(PYTHON) manage.py list_scopes

# Documentation
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "✅ Documentation built in docs/_build/html/"

# CI simulation
ci: lint test
	@echo ""
	@echo "✅ CI checks passed!"

# Quick development setup
dev: install-dev
	@echo ""
	@echo "Quick start commands:"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code"
	@echo "  make lint         - Check code quality"

# Version bump helpers
bump-patch:
	@echo "Bumping patch version..."
	@echo "⚠️  Remember to update:"
	@echo "  - setup.py"
	@echo "  - pyproject.toml"
	@echo "  - drf_scoped_permissions/__init__.py"
	@echo "  - CHANGELOG.md"

bump-minor:
	@echo "Bumping minor version..."
	@echo "⚠️  Remember to update:"
	@echo "  - setup.py"
	@echo "  - pyproject.toml"
	@echo "  - drf_scoped_permissions/__init__.py"
	@echo "  - CHANGELOG.md"

# Pre-commit checks
pre-commit: format lint test
	@echo ""
	@echo "✅ Pre-commit checks passed! Ready to commit."

# Complete workflow for first-time setup
setup: venv install-dev test
	@echo ""
	@echo "🎉 Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate venv: source $(VENV_BIN)/activate"
	@echo "  2. Make changes to the code"
	@echo "  3. Run: make test"
	@echo "  4. Run: make format"
	@echo "  5. Run: make lint"
	@echo "  6. Commit your changes"
