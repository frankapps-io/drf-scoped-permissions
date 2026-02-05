"""
Tests for models.
"""

import pytest
from django.utils import timezone

from drf_scoped_permissions.models import ScopedAPIKey

pytestmark = pytest.mark.django_db


class TestScopedAPIKey:
    """Test ScopedAPIKey model."""

    def test_create_api_key(self):
        """Test creating an API key."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Test Key",
            scopes=["posts.read", "posts.write"]
        )

        assert api_key.name == "Test Key"
        assert api_key.scopes == ["posts.read", "posts.write"]
        assert key is not None
        assert len(key) > 20  # Should be a long key

    def test_has_scope(self):
        """Test has_scope method."""
        api_key = ScopedAPIKey(
            name="Test Key",
            scopes=["posts.read", "posts.write"]
        )

        assert api_key.has_scope("posts.read") is True
        assert api_key.has_scope("posts.write") is True
        assert api_key.has_scope("posts.delete") is False

    def test_unrestricted_key_has_all_scopes(self):
        """Test that keys without scopes have all scopes."""
        api_key = ScopedAPIKey(name="Unrestricted")

        assert api_key.has_scope("posts.read") is True
        assert api_key.has_scope("anything.anything") is True

    def test_str_representation(self):
        """Test string representation."""
        api_key = ScopedAPIKey(
            name="Test Key",
            scopes=["posts.read", "posts.write"]
        )

        assert "Test Key" in str(api_key)
        assert "2 scopes" in str(api_key)

    def test_str_representation_unrestricted(self):
        """Test string representation for unrestricted key."""
        api_key = ScopedAPIKey(name="Unrestricted Key", scopes=[])

        assert "Unrestricted Key" in str(api_key)
        assert "unrestricted" in str(api_key)

    def test_update_last_used(self):
        """Test update_last_used method."""
        api_key, _ = ScopedAPIKey.objects.create_key(
            name="Test Key",
            scopes=["posts.read"]
        )
        assert api_key.last_used_at is None

        before = timezone.now()
        api_key.update_last_used()
        after = timezone.now()

        api_key.refresh_from_db()
        assert api_key.last_used_at is not None
        assert before <= api_key.last_used_at <= after


class TestScopedGroup:
    """Test ScopedGroup model."""

    def test_create_scoped_group(self, group_with_scopes):
        """Test creating a scoped group."""
        scoped_group = group_with_scopes.scoped_group

        assert scoped_group.scopes == ["posts.read", "posts.write"]
        assert scoped_group.group == group_with_scopes

    def test_has_scope(self, group_with_scopes):
        """Test has_scope method."""
        scoped_group = group_with_scopes.scoped_group

        assert scoped_group.has_scope("posts.read") is True
        assert scoped_group.has_scope("posts.write") is True
        assert scoped_group.has_scope("posts.delete") is False

    def test_str_representation(self, group_with_scopes):
        """Test string representation."""
        scoped_group = group_with_scopes.scoped_group

        assert "Test Group" in str(scoped_group)
        assert "2 scopes" in str(scoped_group)
