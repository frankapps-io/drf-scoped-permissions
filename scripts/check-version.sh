#!/bin/sh
set -e

ROOT="$(git rev-parse --show-toplevel)"

PYPROJECT_VERSION=$(grep '^version = ' "$ROOT/pyproject.toml" | head -1 | cut -d'"' -f2)
INIT_VERSION=$(grep '__version__' "$ROOT/drf_scoped_permissions/__init__.py" | cut -d'"' -f2)

if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    echo "🙈  Version mismatch:"
    echo "  · pyproject.toml: $PYPROJECT_VERSION"
    echo "  · __init__.py:    $INIT_VERSION"
    echo "Please ensure both files have the same version."
    exit 1
fi

if ! grep -q "## \[$PYPROJECT_VERSION\]" "$ROOT/CHANGELOG.md" && ! grep -q "## $PYPROJECT_VERSION" "$ROOT/CHANGELOG.md"; then
    echo "🙈  No CHANGELOG.md entry for version $PYPROJECT_VERSION"
    echo "Please add an entry for this version in CHANGELOG.md."
    exit 1
fi

echo "👍  Version $PYPROJECT_VERSION consistent across files."