"""
Tests for utility functions.
"""

import pytest

from drf_scoped_permissions.utils import (
    discover_scopes_from_urls,
    discover_scopes_with_apps,
    get_resource_name,
    get_scopes_grouped_by_app,
    get_scopes_grouped_by_resource,
    get_user_scopes,
)

pytestmark = pytest.mark.django_db


class TestGetResourceName:
    """Test get_resource_name() centralized resolution."""

    def test_explicit_scope_resource(self):
        """scope_resource attribute takes precedence over class name."""
        from tests.views import PostViewSet

        assert get_resource_name(PostViewSet) == "posts"

    def test_scope_resource_on_instance(self):
        """Works with instances, not just classes."""
        from tests.views import PostViewSet

        instance = PostViewSet()
        assert get_resource_name(instance) == "posts"

    def test_fallback_to_class_name(self):
        """Falls back to class name with ViewSet stripped, lowercased."""
        from rest_framework import viewsets

        class OrderItemViewSet(viewsets.ViewSet):
            def list(self, request):
                pass

        assert get_resource_name(OrderItemViewSet) == "orderitem"

    def test_scope_resource_over_class_name(self):
        """scope_resource takes priority over class name fallback."""
        from tests.views import UserProfileViewSet

        # Class name would give "userprofile", but scope_resource = "profiles"
        assert get_resource_name(UserProfileViewSet) == "profiles"


class TestScopeDiscovery:
    """Test scope discovery utilities."""

    def test_discover_scopes_from_urls(self):
        """Test discovering scopes from registered URLs."""
        scopes = discover_scopes_from_urls()

        # PostViewSet has scope_resource = "posts", so must be keyed as "posts"
        assert "posts" in scopes
        assert "posts.read" in scopes["posts"]
        assert "posts.write" in scopes["posts"]
        assert "posts.delete" in scopes["posts"]

    def test_discover_scope_resource_takes_precedence(self):
        """scope_resource should be used instead of basename or class name."""
        scopes = discover_scopes_from_urls()

        # UserProfileViewSet has scope_resource = "profiles"
        # Without the fix, it would be discovered as "user-profile" (basename)
        assert "profiles" in scopes
        assert "profiles.read" in scopes["profiles"]

        # Must NOT appear under the basename or stripped class name
        assert "user-profile" not in scopes
        assert "userprofile" not in scopes

    def test_discover_scopes_with_apps(self):
        """Test that app labels are tracked during discovery."""
        scopes_with_apps = discover_scopes_with_apps()

        assert "posts" in scopes_with_apps
        app_label, scope_list = scopes_with_apps["posts"]
        assert isinstance(app_label, str)
        assert "posts.read" in scope_list

    def test_get_scopes_grouped_by_resource(self):
        """Test getting scopes grouped by resource."""
        grouped = get_scopes_grouped_by_resource()

        assert isinstance(grouped, dict)
        assert len(grouped) > 0

        # Each resource should have a list of (scope, display) tuples
        for _resource, scopes in grouped.items():
            assert isinstance(scopes, list)
            assert len(scopes) > 0
            assert all(isinstance(s, tuple) for s in scopes)

    def test_get_scopes_grouped_by_app(self):
        """Test getting scopes grouped by app then resource."""
        grouped = get_scopes_grouped_by_app()

        assert isinstance(grouped, dict)
        assert len(grouped) > 0

        for app_label, resources in grouped.items():
            assert isinstance(app_label, str)
            assert isinstance(resources, dict)
            for _resource_name, scopes in resources.items():
                assert isinstance(scopes, list)
                assert all(isinstance(s, tuple) and len(s) == 2 for s in scopes)


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
