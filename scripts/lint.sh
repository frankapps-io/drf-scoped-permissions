#!/bin/sh
set -e

echo "Checking code with ruff..."
NEEDS_RESTAGE=0

if ! ruff check drf_scoped_permissions tests; then
    echo ""
    echo "Ruff found lint issues, auto-fixing..."
    ruff check --fix drf_scoped_permissions tests
    NEEDS_RESTAGE=1
fi

if ! ruff format --check drf_scoped_permissions tests > /dev/null 2>&1; then
    echo "Ruff found formatting issues, auto-formatting..."
    ruff format drf_scoped_permissions tests
    NEEDS_RESTAGE=1
fi

if [ "$NEEDS_RESTAGE" = "1" ]; then
    git add -u
    echo "Auto-fixed and re-staged."
fi

echo "Type checking with mypy..."
mypy drf_scoped_permissions

echo ""
echo "All lint checks passed!"