"""
Pytest configuration and fixtures.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from drf_scoped_permissions.models import ScopedAPIKey, ScopedGroup

User = get_user_model()


@pytest.fixture
def api_client():
    """Provide a DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def api_key_unrestricted():
    """Create an unrestricted API key (no scopes)."""
    api_key, key = ScopedAPIKey.objects.create_key(
        name="Unrestricted Test Key"
    )
    # Store the key for tests to use
    api_key._test_key = key
    return api_key


@pytest.fixture
def api_key_with_scopes():
    """Create an API key with specific scopes."""
    api_key, key = ScopedAPIKey.objects.create_key(
        name="Scoped Test Key",
        scopes=["posts.read", "posts.write"]
    )
    # Store the key for tests to use
    api_key._test_key = key
    return api_key


@pytest.fixture
def group_with_scopes():
    """Create a group with scopes."""
    group = Group.objects.create(name="Test Group")
    ScopedGroup.objects.create(
        group=group,
        scopes=["posts.read", "posts.write"]
    )
    return group


@pytest.fixture
def user_with_group(user, group_with_scopes):
    """Create a user with a scoped group."""
    user.groups.add(group_with_scopes)
    return user
