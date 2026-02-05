"""
Tests for utility functions.
"""

import pytest

from drf_scoped_permissions.utils import (
    discover_scopes_from_urls,
    get_scopes_grouped_by_resource,
    get_user_scopes,
)

pytestmark = pytest.mark.django_db


class TestScopeDiscovery:
    """Test scope discovery utilities."""

    def test_discover_scopes_from_urls(self):
        """Test discovering scopes from registered URLs."""
        scopes = discover_scopes_from_urls()

        # Should find the PostViewSet from test URLs
        assert "post" in scopes or "posts" in scopes

        # Check that standard actions are discovered
        resource_scopes = scopes.get("post", scopes.get("posts", []))
        assert any("read" in s for s in resource_scopes)
        assert any("write" in s for s in resource_scopes)
        assert any("delete" in s for s in resource_scopes)

    def test_get_scopes_grouped_by_resource(self):
        """Test getting scopes grouped by resource."""
        grouped = get_scopes_grouped_by_resource()

        assert isinstance(grouped, dict)

        # Should have at least one resource
        assert len(grouped) > 0

        # Each resource should have a list of (scope, display) tuples
        for _resource, scopes in grouped.items():
            assert isinstance(scopes, list)
            assert len(scopes) > 0
            assert all(isinstance(s, tuple) for s in scopes)


class TestUserScopes:
    """Test user scope utilities."""

    def test_get_user_scopes(self, user_with_group):
        """Test getting scopes for a user."""
        scopes = get_user_scopes(user_with_group)

        assert isinstance(scopes, set)
        assert "posts.read" in scopes
        assert "posts.write" in scopes

    def test_get_user_scopes_no_groups(self, user):
        """Test getting scopes for user with no groups."""
        scopes = get_user_scopes(user)

        assert isinstance(scopes, set)
        assert len(scopes) == 0
