"""
Tests for authentication backend.
"""

from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone

from drf_scoped_permissions.models import ScopedAPIKey

pytestmark = pytest.mark.django_db


class TestAPIKeyAuthentication:
    """Test API key authentication."""

    def test_valid_api_key_authenticates(self, api_client):
        """Test that a valid API key authenticates successfully."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Test Key",
            scopes=["posts.read"]
        )
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {key}")

        response = api_client.get("/api/posts/")
        assert response.status_code == 200

    def test_revoked_api_key_fails(self, api_client):
        """Test that a revoked API key fails authentication."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Revoked Key",
            scopes=["posts.read"]
        )
        api_key.revoked = True
        api_key.save()

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {key}")

        response = api_client.get("/api/posts/")
        # Returns 401 - revoked keys are treated as invalid by djangorestframework-api-key
        assert response.status_code == 401

    def test_expired_api_key_fails(self, api_client):
        """Test that an expired API key fails authentication."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Expired Key",
            scopes=["posts.read"]
        )
        # Set expiry to yesterday
        api_key.expiry_date = timezone.now() - timedelta(days=1)
        api_key.save()

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {key}")

        response = api_client.get("/api/posts/")
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_wrong_keyword_returns_none(self, api_client):
        """Test that wrong auth keyword (e.g., Token) is ignored."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Test Key",
            scopes=["posts.read"]
        )
        # Use "Token" instead of "Bearer"
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {key}")

        response = api_client.get("/api/posts/")
        # Should fail because auth returns None (no valid auth found)
        assert response.status_code == 401

    def test_malformed_auth_header_returns_none(self, api_client):
        """Test that malformed auth header is ignored."""
        # No space between keyword and key
        api_client.credentials(HTTP_AUTHORIZATION="Bearer")

        response = api_client.get("/api/posts/")
        assert response.status_code == 401

    def test_no_auth_header_returns_none(self, api_client):
        """Test that missing auth header returns 401."""
        response = api_client.get("/api/posts/")
        assert response.status_code == 401

    @override_settings(SCOPED_PERMISSIONS_TRACK_LAST_USED=True)
    def test_last_used_tracking_when_enabled(self, api_client):
        """Test that last_used_at is updated when tracking is enabled."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Tracked Key",
            scopes=["posts.read"]
        )
        assert api_key.last_used_at is None

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {key}")
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Refresh from database
        api_key.refresh_from_db()
        assert api_key.last_used_at is not None

    @override_settings(SCOPED_PERMISSIONS_TRACK_LAST_USED=False)
    def test_last_used_tracking_disabled_by_default(self, api_client):
        """Test that last_used_at is NOT updated when tracking is disabled."""
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Untracked Key",
            scopes=["posts.read"]
        )
        assert api_key.last_used_at is None

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {key}")
        response = api_client.get("/api/posts/")
        assert response.status_code == 200

        # Refresh from database - should still be None
        api_key.refresh_from_db()
        assert api_key.last_used_at is None
