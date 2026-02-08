"""
Tests for permission classes.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestAPIKeyPermissions:
    """Test API key permissions."""

    def test_unrestricted_api_key_has_full_access(self, api_client, api_key_unrestricted):
        """Test that API key without scopes has full access."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {api_key_unrestricted._test_key}")

        # Should be able to read
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Should be able to write
        response = api_client.post("/api/posts/", {"title": "New Post"})
        assert response.status_code == 200

        # Should be able to delete
        response = api_client.delete("/api/posts/1/")
        assert response.status_code == 204

    def test_scoped_api_key_allows_permitted_actions(self, api_client, api_key_with_scopes):
        """Test that scoped API key allows only permitted actions."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {api_key_with_scopes._test_key}")

        # Should be able to read (posts.read)
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Should be able to write (posts.write)
        response = api_client.post("/api/posts/", {"title": "New Post"})
        assert response.status_code == 200

    def test_scoped_api_key_denies_unpermitted_actions(self, api_client, api_key_with_scopes):
        """Test that scoped API key denies unpermitted actions."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {api_key_with_scopes._test_key}")

        # Should NOT be able to delete (posts.delete not in scopes)
        response = api_client.delete("/api/posts/1/")
        assert response.status_code == 403

    def test_invalid_api_key_denied(self, api_client):
        """Test that invalid API key is denied."""
        api_client.credentials(HTTP_AUTHORIZATION="Api-Key invalid-key-123")

        response = api_client.get("/api/posts/")
        # 401 is returned because authentication fails (invalid key)
        assert response.status_code == 401


class TestUserGroupPermissions:
    """Test user group-based permissions."""

    def test_user_with_group_scopes_allowed(self, api_client, user_with_group):
        """Test that user with group scopes is allowed."""
        api_client.force_authenticate(user=user_with_group)

        # Should be able to read
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Should be able to write
        response = api_client.post("/api/posts/", {"title": "New Post"})
        assert response.status_code == 200

    def test_user_with_group_scopes_denied(self, api_client, user_with_group):
        """Test that user without proper scope is denied."""
        api_client.force_authenticate(user=user_with_group)

        # Should NOT be able to delete (posts.delete not in group scopes)
        response = api_client.delete("/api/posts/1/")
        assert response.status_code == 403

    def test_user_without_groups_denied(self, api_client, user):
        """Test that user without groups is denied."""
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/posts/")
        assert response.status_code == 403

    def test_superuser_always_allowed(self, api_client):
        """Test that superusers bypass all checks."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

        api_client.force_authenticate(user=superuser)

        # Should be able to do everything
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        response = api_client.post("/api/posts/", {"title": "New Post"})
        assert response.status_code == 200

        response = api_client.delete("/api/posts/1/")
        assert response.status_code == 204


class TestCustomActions:
    """Test custom action permissions."""

    def test_custom_action_requires_scope(self, api_client, api_key_with_scopes):
        """Test that custom actions require specific scopes."""
        # API key has posts.read and posts.write, but not posts.publish
        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {api_key_with_scopes._test_key}")

        response = api_client.post("/api/posts/1/publish/")
        assert response.status_code == 403

    def test_custom_action_allowed_with_scope(self, api_client):
        """Test that custom actions work with proper scope."""
        from drf_scoped_permissions.models import ScopedAPIKey

        # Create key with publish scope
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Publisher Key", scopes=["posts.read", "posts.publish"]
        )

        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")

        response = api_client.post("/api/posts/1/publish/")
        assert response.status_code == 200


class TestRetrieveAndUpdateActions:
    """Test retrieve and update action permissions."""

    def test_retrieve_requires_read_scope(self, api_client):
        """Test that retrieve action requires read scope."""
        from drf_scoped_permissions.models import ScopedAPIKey

        # Key with only write scope
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Write Only Key", scopes=["posts.write"]
        )

        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")

        # Retrieve should fail (needs posts.read)
        response = api_client.get("/api/posts/1/")
        assert response.status_code == 403

    def test_update_requires_write_scope(self, api_client):
        """Test that update action requires write scope."""
        from drf_scoped_permissions.models import ScopedAPIKey

        # Key with only read scope
        api_key, key = ScopedAPIKey.objects.create_key(name="Read Only Key", scopes=["posts.read"])

        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")

        # PUT should fail (needs posts.write)
        response = api_client.put("/api/posts/1/", {"title": "Updated"})
        assert response.status_code == 403

        # PATCH should also fail
        response = api_client.patch("/api/posts/1/", {"title": "Updated"})
        assert response.status_code == 403

    def test_update_allowed_with_write_scope(self, api_client, api_key_with_scopes):
        """Test that update works with write scope."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {api_key_with_scopes._test_key}")

        # PUT should work (has posts.write)
        response = api_client.put("/api/posts/1/", {"title": "Updated"})
        assert response.status_code == 200

        # PATCH should also work
        response = api_client.patch("/api/posts/1/", {"title": "Updated"})
        assert response.status_code == 200


class TestMultipleGroups:
    """Test permissions with multiple groups."""

    def test_user_with_multiple_groups_gets_combined_scopes(self, api_client, user):
        """Test that user scopes are combined from all groups."""
        from django.contrib.auth.models import Group

        from drf_scoped_permissions.models import ScopedGroup

        # Create two groups with different scopes
        readers = Group.objects.create(name="Readers")
        ScopedGroup.objects.create(group=readers, scopes=["posts.read"])

        deleters = Group.objects.create(name="Deleters")
        ScopedGroup.objects.create(group=deleters, scopes=["posts.delete"])

        # Add user to both groups
        user.groups.add(readers, deleters)

        api_client.force_authenticate(user=user)

        # Should be able to read (from Readers group)
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Should be able to delete (from Deleters group)
        response = api_client.delete("/api/posts/1/")
        assert response.status_code == 204

        # Should NOT be able to write (not in either group)
        response = api_client.post("/api/posts/", {"title": "New"})
        assert response.status_code == 403
